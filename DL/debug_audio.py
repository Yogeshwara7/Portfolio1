#!/usr/bin/env python3
"""
Audio debugging utility for Voice Recognition System
"""

import os
import sys
import numpy as np
import soundfile as sf
import librosa
from preprocessing import AudioPreprocessor

def analyze_audio_file(file_path):
    """Analyze an audio file and print detailed information"""
    print(f"🔍 Analyzing audio file: {file_path}")
    print("=" * 60)
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ File does not exist: {file_path}")
        return False
    
    # Check file size
    file_size = os.path.getsize(file_path)
    print(f"📊 File size: {file_size} bytes")
    
    if file_size == 0:
        print("❌ File is empty!")
        return False
    
    # Try to read with soundfile
    try:
        print("\n🎵 Reading with soundfile...")
        audio_sf, sr_sf = sf.read(file_path)
        print(f"✅ Soundfile read successful")
        print(f"   Shape: {audio_sf.shape}")
        print(f"   Sample rate: {sr_sf}")
        print(f"   Duration: {len(audio_sf)/sr_sf:.2f} seconds")
        print(f"   Data type: {audio_sf.dtype}")
        print(f"   Range: [{audio_sf.min():.4f}, {audio_sf.max():.4f}]")
        
    except Exception as e:
        print(f"❌ Soundfile read failed: {e}")
        return False
    
    # Try to read with librosa
    try:
        print("\n🎵 Reading with librosa...")
        audio_lr, sr_lr = librosa.load(file_path, sr=None)
        print(f"✅ Librosa read successful")
        print(f"   Shape: {audio_lr.shape}")
        print(f"   Sample rate: {sr_lr}")
        print(f"   Duration: {len(audio_lr)/sr_lr:.2f} seconds")
        print(f"   Data type: {audio_lr.dtype}")
        print(f"   Range: [{audio_lr.min():.4f}, {audio_lr.max():.4f}]")
        
    except Exception as e:
        print(f"❌ Librosa read failed: {e}")
        return False
    
    # Test preprocessing
    try:
        print("\n🔄 Testing preprocessing...")
        preprocessor = AudioPreprocessor()
        features = preprocessor.preprocess_audio(file_path, feature_type='spectrogram')
        
        if features is not None:
            print(f"✅ Preprocessing successful")
            print(f"   Features shape: {features.shape}")
            print(f"   Features range: [{features.min():.2f}, {features.max():.2f}]")
        else:
            print(f"❌ Preprocessing failed")
            return False
            
    except Exception as e:
        print(f"❌ Preprocessing error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False
    
    print(f"\n✅ Audio file analysis completed successfully!")
    return True

def test_audio_recording():
    """Test audio recording functionality"""
    print("🎤 Testing audio recording...")
    
    try:
        import sounddevice as sd
        
        # List audio devices
        print("\n🔊 Available audio devices:")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"   {i}: {device['name']} (Input channels: {device['max_input_channels']})")
        
        # Test recording
        print(f"\n🎤 Testing 2-second recording...")
        sample_rate = 22050
        duration = 2
        
        print(f"Recording in 3... 2... 1...")
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait()
        
        print(f"✅ Recording completed")
        print(f"   Shape: {audio_data.shape}")
        print(f"   Range: [{audio_data.min():.4f}, {audio_data.max():.4f}]")
        
        # Save test recording
        test_file = "test_recording.wav"
        sf.write(test_file, audio_data.flatten(), sample_rate)
        print(f"💾 Test recording saved as: {test_file}")
        
        # Analyze the test recording
        return analyze_audio_file(test_file)
        
    except Exception as e:
        print(f"❌ Recording test failed: {e}")
        return False

def check_dependencies():
    """Check if all required packages are available"""
    print("📦 Checking dependencies...")
    
    packages = [
        ('numpy', 'np'),
        ('librosa', 'librosa'),
        ('soundfile', 'sf'),
        ('sounddevice', 'sd'),
        ('sklearn', 'sklearn')
    ]
    
    all_good = True
    for package_name, import_name in packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - NOT INSTALLED")
            all_good = False
    
    return all_good

def main():
    print("🎤 Voice Recognition System - Audio Debug Tool")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Some dependencies are missing. Please install them first.")
        return
    
    if len(sys.argv) > 1:
        # Analyze specific file
        file_path = sys.argv[1]
        analyze_audio_file(file_path)
    else:
        # Interactive mode
        print("\nOptions:")
        print("1. Test audio recording")
        print("2. Analyze audio file")
        print("3. Check temp_audio directory")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            test_audio_recording()
        elif choice == '2':
            file_path = input("Enter audio file path: ").strip()
            analyze_audio_file(file_path)
        elif choice == '3':
            temp_dir = 'temp_audio'
            if os.path.exists(temp_dir):
                files = [f for f in os.listdir(temp_dir) if f.endswith('.wav')]
                print(f"\n📁 Files in {temp_dir}:")
                for i, file in enumerate(files):
                    print(f"   {i+1}. {file}")
                
                if files:
                    try:
                        file_num = int(input(f"\nSelect file to analyze (1-{len(files)}): ")) - 1
                        if 0 <= file_num < len(files):
                            analyze_audio_file(os.path.join(temp_dir, files[file_num]))
                    except ValueError:
                        print("Invalid selection")
                else:
                    print("   No .wav files found")
            else:
                print(f"❌ Directory {temp_dir} does not exist")

if __name__ == "__main__":
    main()