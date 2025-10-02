import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import time
import os

class AudioRecorder:
    def __init__(self, sample_rate=22050, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.recording = False
        self.audio_data = []
        
    def record_audio(self, duration=5, output_file=None):
        """Record audio for specified duration"""
        print(f"Recording for {duration} seconds...")
        print("Please speak: 'Login My Account'")
        
        # Record audio
        audio_data = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='float32'
        )
        
        # Wait for recording to complete
        sd.wait()
        
        # Flatten if stereo
        if len(audio_data.shape) > 1:
            audio_data = audio_data.flatten()
        
        print("Recording completed!")
        
        # Save to file if specified
        if output_file:
            sf.write(output_file, audio_data, self.sample_rate)
            print(f"Audio saved to {output_file}")
        
        return audio_data
    
    def record_with_voice_activity_detection(self, max_duration=10, silence_threshold=0.01, silence_duration=2):
        """Record audio with automatic stop on silence"""
        print("Recording started. Speak now...")
        print("Recording will stop automatically after silence.")
        
        chunk_size = int(0.1 * self.sample_rate)  # 100ms chunks
        audio_chunks = []
        silence_counter = 0
        max_silence_chunks = int(silence_duration / 0.1)
        
        stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='float32'
        )
        
        with stream:
            for _ in range(int(max_duration / 0.1)):
                chunk, _ = stream.read(chunk_size)
                audio_chunks.append(chunk.flatten())
                
                # Check for silence
                if np.max(np.abs(chunk)) < silence_threshold:
                    silence_counter += 1
                else:
                    silence_counter = 0
                
                # Stop if silence detected for specified duration
                if silence_counter >= max_silence_chunks and len(audio_chunks) > 10:
                    break
        
        print("Recording completed!")
        
        # Concatenate all chunks
        audio_data = np.concatenate(audio_chunks)
        return audio_data
    
    def play_audio(self, audio_data):
        """Play recorded audio"""
        print("Playing recorded audio...")
        sd.play(audio_data, self.sample_rate)
        sd.wait()
        print("Playback completed!")
    
    def save_audio(self, audio_data, filename):
        """Save audio data to file"""
        sf.write(filename, audio_data, self.sample_rate)
        print(f"Audio saved to {filename}")
    
    def load_audio(self, filename):
        """Load audio from file"""
        audio_data, sr = sf.read(filename)
        if sr != self.sample_rate:
            print(f"Warning: File sample rate ({sr}) differs from recorder sample rate ({self.sample_rate})")
        return audio_data
    
    def get_audio_info(self, audio_data):
        """Get information about audio data"""
        duration = len(audio_data) / self.sample_rate
        max_amplitude = np.max(np.abs(audio_data))
        rms = np.sqrt(np.mean(audio_data**2))
        
        return {
            'duration': duration,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'max_amplitude': max_amplitude,
            'rms': rms,
            'samples': len(audio_data)
        }
    
    def list_audio_devices(self):
        """List available audio input devices"""
        devices = sd.query_devices()
        print("Available audio devices:")
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"{i}: {device['name']} (Input channels: {device['max_input_channels']})")
    
    def set_input_device(self, device_id):
        """Set specific input device"""
        sd.default.device[0] = device_id
        print(f"Input device set to: {sd.query_devices(device_id)['name']}")