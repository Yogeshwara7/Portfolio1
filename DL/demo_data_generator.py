#!/usr/bin/env python3
"""
Demo Data Generator for Voice Recognition System
Creates synthetic voice data for testing when real voice samples aren't available
"""

import numpy as np
import librosa
import soundfile as sf
import os
from preprocessing import AudioPreprocessor
from database import VoiceDatabase

class DemoDataGenerator:
    def __init__(self):
        self.preprocessor = AudioPreprocessor()
        self.db = VoiceDatabase()
        self.sample_rate = 22050
        
    def generate_synthetic_voice(self, duration=5, base_freq=150, noise_level=0.1):
        """Generate synthetic voice-like audio signal"""
        t = np.linspace(0, duration, int(duration * self.sample_rate))
        
        # Create fundamental frequency with some variation
        freq_variation = np.sin(2 * np.pi * 2 * t) * 20  # 2 Hz variation
        fundamental = base_freq + freq_variation
        
        # Generate harmonics (typical for human voice)
        signal = np.zeros_like(t)
        harmonics = [1, 0.5, 0.3, 0.2, 0.1]  # Harmonic amplitudes
        
        for i, amplitude in enumerate(harmonics):
            harmonic_freq = fundamental * (i + 1)
            signal += amplitude * np.sin(2 * np.pi * harmonic_freq * t)
        
        # Add formant-like filtering (simulate vocal tract)
        # Simple bandpass filtering effect
        formant1 = 0.3 * np.sin(2 * np.pi * 800 * t)
        formant2 = 0.2 * np.sin(2 * np.pi * 1200 * t)
        signal = signal + formant1 + formant2
        
        # Add some noise for realism
        noise = np.random.normal(0, noise_level, len(signal))
        signal += noise
        
        # Apply envelope (voice-like amplitude modulation)
        envelope = self.create_voice_envelope(t, duration)
        signal *= envelope
        
        # Normalize
        signal = signal / np.max(np.abs(signal)) * 0.8
        
        return signal.astype(np.float32)
    
    def create_voice_envelope(self, t, duration):
        """Create a voice-like amplitude envelope"""
        # Simulate speech pattern with pauses and emphasis
        envelope = np.ones_like(t)
        
        # Add some speech-like modulation
        speech_pattern = np.sin(2 * np.pi * 3 * t) * 0.3 + 0.7  # 3 Hz modulation
        
        # Add attack and decay
        attack_time = 0.1
        decay_time = 0.2
        
        # Attack
        attack_mask = t < attack_time
        envelope[attack_mask] = t[attack_mask] / attack_time
        
        # Decay at the end
        decay_start = duration - decay_time
        decay_mask = t > decay_start
        envelope[decay_mask] = (duration - t[decay_mask]) / decay_time
        
        # Apply speech pattern
        envelope *= speech_pattern
        
        # Ensure non-negative
        envelope = np.maximum(envelope, 0.1)
        
        return envelope
    
    def create_demo_students(self, num_students=5):
        """Create demo students with synthetic voice data"""
        demo_students = [
            {"id": "DEMO001", "name": "Alice Johnson", "email": "alice@demo.edu", "base_freq": 220},
            {"id": "DEMO002", "name": "Bob Smith", "email": "bob@demo.edu", "base_freq": 150},
            {"id": "DEMO003", "name": "Carol Davis", "email": "carol@demo.edu", "base_freq": 200},
            {"id": "DEMO004", "name": "David Wilson", "email": "david@demo.edu", "base_freq": 130},
            {"id": "DEMO005", "name": "Emma Brown", "email": "emma@demo.edu", "base_freq": 250},
        ]
        
        print("🎭 Generating Demo Students with Synthetic Voice Data")
        print("=" * 55)
        
        for i, student in enumerate(demo_students[:num_students]):
            print(f"\nCreating student {i+1}/{num_students}: {student['name']}")
            
            # Register student
            if self.db.register_student(student['id'], student['name'], student['email']):
                print(f"✅ Registered {student['name']}")
                
                # Generate multiple voice samples for better training
                for sample_num in range(3):
                    print(f"  Generating voice sample {sample_num + 1}/3...")
                    
                    # Generate synthetic voice with slight variations
                    base_freq = student['base_freq'] + np.random.normal(0, 10)  # Add variation
                    noise_level = 0.05 + np.random.uniform(0, 0.05)  # Vary noise
                    
                    synthetic_voice = self.generate_synthetic_voice(
                        duration=5, 
                        base_freq=base_freq, 
                        noise_level=noise_level
                    )
                    
                    # Save temporary audio file
                    temp_file = f"temp_demo_{student['id']}_{sample_num}.wav"
                    sf.write(temp_file, synthetic_voice, self.sample_rate)
                    
                    # Process and store
                    features = self.preprocessor.preprocess_audio(temp_file, feature_type='spectrogram')
                    
                    if features is not None:
                        self.db.store_voice_embedding(student['id'], features, synthetic_voice)
                        print(f"  ✅ Voice sample {sample_num + 1} stored")
                    else:
                        print(f"  ❌ Failed to process voice sample {sample_num + 1}")
                    
                    # Clean up
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                
                print(f"✅ Completed {student['name']}")
            else:
                print(f"❌ Failed to register {student['name']}")
        
        print(f"\n🎉 Demo data generation completed!")
        print(f"Created {num_students} demo students with synthetic voice data")
        print("You can now train the model and test the system!")
    
    def generate_test_audio_files(self, output_dir="demo_audio"):
        """Generate test audio files for manual testing"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        print(f"\n🎵 Generating test audio files in '{output_dir}' directory")
        
        test_voices = [
            {"name": "high_pitch_female", "base_freq": 250, "noise": 0.05},
            {"name": "medium_pitch_male", "base_freq": 150, "noise": 0.08},
            {"name": "low_pitch_male", "base_freq": 120, "noise": 0.06},
            {"name": "noisy_sample", "base_freq": 180, "noise": 0.15},
        ]
        
        for voice in test_voices:
            print(f"  Creating {voice['name']}.wav...")
            
            synthetic_voice = self.generate_synthetic_voice(
                duration=5,
                base_freq=voice['base_freq'],
                noise_level=voice['noise']
            )
            
            output_file = os.path.join(output_dir, f"{voice['name']}.wav")
            sf.write(output_file, synthetic_voice, self.sample_rate)
        
        print(f"✅ Test audio files created in '{output_dir}' directory")
    
    def analyze_voice_characteristics(self, audio_data):
        """Analyze characteristics of generated voice"""
        # Basic audio analysis
        duration = len(audio_data) / self.sample_rate
        rms = np.sqrt(np.mean(audio_data**2))
        max_amplitude = np.max(np.abs(audio_data))
        
        # Spectral analysis
        fft = np.fft.fft(audio_data)
        freqs = np.fft.fftfreq(len(fft), 1/self.sample_rate)
        magnitude = np.abs(fft)
        
        # Find dominant frequency
        dominant_freq_idx = np.argmax(magnitude[:len(magnitude)//2])
        dominant_freq = freqs[dominant_freq_idx]
        
        return {
            'duration': duration,
            'rms': rms,
            'max_amplitude': max_amplitude,
            'dominant_frequency': abs(dominant_freq),
            'sample_rate': self.sample_rate
        }
    
    def cleanup_demo_data(self):
        """Remove all demo students and their data"""
        print("\n🧹 Cleaning up demo data...")
        
        students = self.db.list_all_students()
        demo_students = [s for s in students if s['student_id'].startswith('DEMO')]
        
        if not demo_students:
            print("No demo students found")
            return
        
        for student in demo_students:
            if self.db.delete_student(student['student_id']):
                print(f"✅ Deleted {student['name']} ({student['student_id']})")
            else:
                print(f"❌ Failed to delete {student['name']}")
        
        print("🎉 Demo data cleanup completed!")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Demo Data Generator for Voice Recognition System")
    parser.add_argument('--create', type=int, default=5, help='Create N demo students (default: 5)')
    parser.add_argument('--audio-files', action='store_true', help='Generate test audio files')
    parser.add_argument('--cleanup', action='store_true', help='Remove all demo data')
    parser.add_argument('--analyze', help='Analyze audio file characteristics')
    
    args = parser.parse_args()
    
    generator = DemoDataGenerator()
    
    if args.cleanup:
        generator.cleanup_demo_data()
    elif args.audio_files:
        generator.generate_test_audio_files()
    elif args.analyze:
        if os.path.exists(args.analyze):
            audio_data, sr = sf.read(args.analyze)
            characteristics = generator.analyze_voice_characteristics(audio_data)
            
            print(f"\n🔍 Audio Analysis: {args.analyze}")
            print("-" * 40)
            for key, value in characteristics.items():
                if isinstance(value, float):
                    print(f"{key}: {value:.4f}")
                else:
                    print(f"{key}: {value}")
        else:
            print(f"❌ File not found: {args.analyze}")
    else:
        generator.create_demo_students(args.create)

if __name__ == "__main__":
    main()