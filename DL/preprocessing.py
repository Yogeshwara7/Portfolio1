import librosa
import numpy as np
import soundfile as sf
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import os

class AudioPreprocessor:
    def __init__(self, sample_rate=22050, n_mfcc=13, n_fft=2048, hop_length=512, max_length=100):
        self.sample_rate = sample_rate
        self.n_mfcc = n_mfcc
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.max_length = max_length
        self.scaler = StandardScaler()
        
    def load_audio(self, file_path):
        """Load audio file and resample to target sample rate"""
        try:
            print(f"🔄 [PREPROCESSING] Loading audio file: {file_path}")
            
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"❌ [ERROR] Audio file does not exist: {file_path}")
                return None
            
            # Check file size
            file_size = os.path.getsize(file_path)
            print(f"📊 [DEBUG] Audio file size: {file_size} bytes")
            
            if file_size == 0:
                print(f"❌ [ERROR] Audio file is empty: {file_path}")
                return None
            
            # Load audio with librosa
            audio, sr = librosa.load(file_path, sr=self.sample_rate)
            print(f"✅ [DEBUG] Audio loaded successfully")
            print(f"📊 [DEBUG] Original sample rate: {sr}, Target: {self.sample_rate}")
            print(f"📊 [DEBUG] Audio length: {len(audio)} samples ({len(audio)/sr:.2f} seconds)")
            print(f"📊 [DEBUG] Audio range: [{audio.min():.4f}, {audio.max():.4f}]")
            
            return audio
        except Exception as e:
            print(f"❌ [ERROR] Error loading audio file {file_path}: {e}")
            import traceback
            print(f"📋 [DEBUG] Traceback: {traceback.format_exc()}")
            return None
    
    def extract_mfcc(self, audio):
        """Extract MFCC features from audio"""
        mfcc = librosa.feature.mfcc(
            y=audio, 
            sr=self.sample_rate, 
            n_mfcc=self.n_mfcc,
            n_fft=self.n_fft,
            hop_length=self.hop_length
        )
        return mfcc.T  # Transpose to have time frames as rows
    
    def extract_spectrogram(self, audio):
        """Extract mel-spectrogram from audio"""
        try:
            print(f"🔄 [PREPROCESSING] Extracting mel-spectrogram...")
            print(f"📊 [DEBUG] Audio shape: {audio.shape}")
            print(f"📊 [DEBUG] Audio stats: mean={audio.mean():.4f}, std={audio.std():.4f}")
            
            mel_spec = librosa.feature.melspectrogram(
                y=audio,
                sr=self.sample_rate,
                n_fft=self.n_fft,
                hop_length=self.hop_length,
                n_mels=128
            )
            
            print(f"📊 [DEBUG] Mel-spectrogram shape: {mel_spec.shape}")
            print(f"📊 [DEBUG] Mel-spec range: [{mel_spec.min():.4f}, {mel_spec.max():.4f}]")
            
            # Convert to log scale (dB)
            log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
            print(f"📊 [DEBUG] Log mel-spec shape: {log_mel_spec.shape}")
            print(f"📊 [DEBUG] Log mel-spec range: [{log_mel_spec.min():.2f}, {log_mel_spec.max():.2f}] dB")
            
            result = log_mel_spec.T
            print(f"✅ [DEBUG] Spectrogram extracted, final shape: {result.shape}")
            return result
            
        except Exception as e:
            print(f"❌ [ERROR] Error extracting spectrogram: {e}")
            import traceback
            print(f"📋 [DEBUG] Traceback: {traceback.format_exc()}")
            return None
    
    def pad_sequence(self, features):
        """Pad or truncate features to fixed length"""
        if len(features) > self.max_length:
            return features[:self.max_length]
        else:
            pad_width = self.max_length - len(features)
            return np.pad(features, ((0, pad_width), (0, 0)), mode='constant')
    
    def normalize_features(self, features):
        """Normalize features using StandardScaler"""
        original_shape = features.shape
        features_flat = features.reshape(-1, features.shape[-1])
        features_normalized = self.scaler.fit_transform(features_flat)
        return features_normalized.reshape(original_shape)
    
    def preprocess_audio(self, audio_path, feature_type='mfcc'):
        """Complete preprocessing pipeline"""
        try:
            print(f"🚀 [PREPROCESSING] Starting audio preprocessing pipeline")
            print(f"📁 [DEBUG] Input file: {audio_path}")
            print(f"🎛️ [DEBUG] Feature type: {feature_type}")
            
            # Load audio
            audio = self.load_audio(audio_path)
            if audio is None:
                print(f"❌ [ERROR] Failed to load audio")
                return None
            
            # Check if audio has content
            if len(audio) == 0:
                print(f"❌ [ERROR] Audio is empty after loading")
                return None
            
            # Remove silence
            print(f"🔇 [PREPROCESSING] Removing silence...")
            audio = self.remove_silence(audio)
            
            if len(audio) == 0:
                print(f"❌ [ERROR] No audio left after silence removal")
                return None
            
            # Extract features
            print(f"🎵 [PREPROCESSING] Extracting {feature_type} features...")
            if feature_type == 'mfcc':
                features = self.extract_mfcc(audio)
            elif feature_type == 'spectrogram':
                features = self.extract_spectrogram(audio)
            else:
                raise ValueError("feature_type must be 'mfcc' or 'spectrogram'")
            
            if features is None:
                print(f"❌ [ERROR] Feature extraction returned None")
                return None
            
            # Pad to fixed length
            print(f"📏 [PREPROCESSING] Padding sequence to fixed length...")
            print(f"📊 [DEBUG] Features shape before padding: {features.shape}")
            features = self.pad_sequence(features)
            print(f"📊 [DEBUG] Features shape after padding: {features.shape}")
            
            print(f"✅ [SUCCESS] Audio preprocessing completed successfully")
            return features
            
        except Exception as e:
            print(f"💥 [CRITICAL ERROR] Preprocessing pipeline failed: {e}")
            import traceback
            print(f"📋 [DEBUG] Full traceback: {traceback.format_exc()}")
            return None
    
    def remove_silence(self, audio, threshold=0.01):
        """Remove silence from audio"""
        try:
            print(f"🔄 [PREPROCESSING] Removing silence (threshold: {threshold})")
            print(f"📊 [DEBUG] Original audio length: {len(audio)} samples")
            
            # Simple energy-based silence removal
            energy = np.abs(audio)
            mask = energy > threshold
            
            active_samples = np.sum(mask)
            print(f"📊 [DEBUG] Active samples: {active_samples}/{len(audio)} ({active_samples/len(audio)*100:.1f}%)")
            
            if np.any(mask):
                result = audio[mask]
                print(f"✅ [DEBUG] Silence removed, new length: {len(result)} samples")
                return result
            else:
                print(f"⚠️ [WARNING] No audio above threshold, returning original")
                return audio
                
        except Exception as e:
            print(f"❌ [ERROR] Error removing silence: {e}")
            return audio
    
    def save_spectrogram_image(self, spectrogram, output_path):
        """Save spectrogram as image for CNN input"""
        plt.figure(figsize=(10, 4))
        plt.imshow(spectrogram.T, aspect='auto', origin='lower', cmap='viridis')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0, dpi=100)
        plt.close()