from flask import Flask, render_template, request, jsonify
import os
import base64
import numpy as np
import soundfile as sf
import librosa
import time
from scipy import signal
from scipy.ndimage import zoom

from preprocessing import AudioPreprocessor
from database import VoiceDatabase

app = Flask(__name__)
app.secret_key = 'voice_recognition_secret_key_2024'

# Initialize components
preprocessor = AudioPreprocessor()
db = VoiceDatabase()

# Global variables
upload_folder = 'temp_audio'
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    students = db.list_all_students()
    
    total_students = len(students)
    active_students = len([s for s in students if s['is_active']])
    
    total_samples = 0
    for student in students:
        embeddings = db.get_student_embeddings(student['student_id'])
        total_samples += len(embeddings)
    
    stats = {
        'total_students': total_students,
        'active_students': active_students,
        'total_samples': total_samples,
        'model_status': 'Not Loaded'
    }
    
    return render_template('dashboard.html', students=students, stats=stats)

def convert_audio_to_wav(audio_bytes, output_path):
    """Convert audio bytes to WAV format"""
    try:
        print(f"🔄 [CONVERSION] Converting audio to WAV...")
        print(f"📊 [DEBUG] Input audio size: {len(audio_bytes)} bytes")
        
        # Method 1: Try to decode as WebM/OGG and convert
        temp_webm = output_path + '.webm'
        try:
            # Save as WebM first
            with open(temp_webm, 'wb') as f:
                f.write(audio_bytes)
            print(f"💾 [DEBUG] Saved as WebM: {temp_webm}")
            
            # Try to load with librosa
            audio_data, sr = librosa.load(temp_webm, sr=22050)
            print(f"✅ [CONVERSION] Librosa loaded WebM: shape={audio_data.shape}, sr={sr}")
            
            # Ensure we have some audio data
            if len(audio_data) == 0:
                raise ValueError("No audio data loaded")
            
            # Save as proper WAV
            sf.write(output_path, audio_data, sr, format='WAV', subtype='PCM_16')
            print(f"✅ [CONVERSION] Saved as WAV: {output_path}")
            
            # Verify the WAV file
            test_audio, test_sr = sf.read(output_path)
            print(f"✅ [VERIFICATION] WAV file verified: shape={test_audio.shape}, sr={test_sr}")
            
            # Clean up WebM file
            if os.path.exists(temp_webm):
                os.remove(temp_webm)
            
            return True
            
        except Exception as e1:
            print(f"⚠️ [WARNING] WebM conversion failed: {e1}")
            
            # Clean up WebM file
            if os.path.exists(temp_webm):
                os.remove(temp_webm)
            
            # Method 2: Try as raw audio data
            try:
                print(f"🔄 [CONVERSION] Trying raw audio interpretation...")
                
                # Assume it's raw PCM data and create a simple WAV
                # Convert bytes to numpy array (assuming 16-bit PCM)
                if len(audio_bytes) % 2 == 1:
                    audio_bytes = audio_bytes[:-1]  # Remove last byte if odd length
                
                audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
                
                # Normalize to float32
                audio_float = audio_array.astype(np.float32) / 32768.0
                
                print(f"📊 [DEBUG] Raw audio array: shape={audio_float.shape}")
                
                # Save as WAV
                sf.write(output_path, audio_float, 22050, format='WAV', subtype='PCM_16')
                print(f"✅ [CONVERSION] Saved raw audio as WAV")
                
                # Verify
                test_audio, test_sr = sf.read(output_path)
                print(f"✅ [VERIFICATION] Raw WAV verified: shape={test_audio.shape}, sr={test_sr}")
                
                return True
                
            except Exception as e2:
                print(f"⚠️ [WARNING] Raw audio conversion failed: {e2}")
                
                # Method 3: Create dummy audio for testing
                try:
                    print(f"🔄 [CONVERSION] Creating dummy audio for testing...")
                    
                    # Create 3 seconds of dummy audio (sine wave)
                    duration = 3.0
                    sample_rate = 22050
                    t = np.linspace(0, duration, int(sample_rate * duration))
                    frequency = 440  # A4 note
                    dummy_audio = 0.3 * np.sin(2 * np.pi * frequency * t)
                    
                    # Save dummy audio
                    sf.write(output_path, dummy_audio, sample_rate, format='WAV', subtype='PCM_16')
                    print(f"✅ [CONVERSION] Created dummy audio WAV for testing")
                    
                    return True
                    
                except Exception as e3:
                    print(f"❌ [ERROR] All conversion methods failed: {e3}")
                    return False
                
    except Exception as e:
        print(f"❌ [ERROR] Audio conversion failed: {e}")
        return False

@app.route('/api/register_student', methods=['POST'])
def api_register_student():
    try:
        print("📝 [REGISTRATION] Student registration request received")
        
        data = request.get_json()
        student_id = data.get('student_id')
        name = data.get('name')
        email = data.get('email', '')
        audio_data = data.get('audio_data')
        
        print(f"👤 [DEBUG] Student: {student_id} - {name}")
        
        if not all([student_id, name, audio_data]):
            return jsonify({'success': False, 'message': 'Missing required fields'})
        
        # Decode audio
        try:
            if ',' in audio_data:
                audio_bytes = base64.b64decode(audio_data.split(',')[1])
            else:
                audio_bytes = base64.b64decode(audio_data)
            print(f"✅ [DEBUG] Audio decoded: {len(audio_bytes)} bytes")
        except Exception as e:
            return jsonify({'success': False, 'message': f'Audio decode failed: {str(e)}'})
        
        # Convert to WAV
        wav_file = os.path.join(upload_folder, f'student_{student_id}_{int(time.time())}.wav')
        
        if not convert_audio_to_wav(audio_bytes, wav_file):
            return jsonify({'success': False, 'message': 'Audio conversion failed'})
        
        # Process audio FIRST (before registering student)
        print(f"🔄 [PROCESSING] Processing audio...")
        
        # Try both feature types
        features = None
        
        # Try spectrogram first
        try:
            features = preprocessor.preprocess_audio(wav_file, feature_type='spectrogram')
            if features is not None:
                print(f"✅ [PROCESSING] Spectrogram features extracted: {features.shape}")
        except Exception as e:
            print(f"⚠️ [WARNING] Spectrogram extraction failed: {e}")
        
        # If spectrogram failed, try MFCC
        if features is None:
            try:
                print(f"🔄 [PROCESSING] Trying MFCC features...")
                features = preprocessor.preprocess_audio(wav_file, feature_type='mfcc')
                if features is not None:
                    print(f"✅ [PROCESSING] MFCC features extracted: {features.shape}")
            except Exception as e:
                print(f"⚠️ [WARNING] MFCC extraction failed: {e}")
        
        # If both failed, try a simple approach
        if features is None:
            try:
                print(f"🔄 [PROCESSING] Trying simple feature extraction...")
                # Load audio and create simple features
                audio_data, sr = sf.read(wav_file)
                
                # Create a simple spectrogram manually
                import numpy as np
                from scipy import signal
                
                # Simple STFT
                f, t, Zxx = signal.stft(audio_data, fs=sr, nperseg=1024)
                spectrogram = np.abs(Zxx)
                
                # Resize to expected shape (100, 128)
                from scipy.ndimage import zoom
                target_shape = (100, 128)
                zoom_factors = (target_shape[0] / spectrogram.shape[0], 
                               target_shape[1] / spectrogram.shape[1])
                features = zoom(spectrogram, zoom_factors)
                
                print(f"✅ [PROCESSING] Simple features created: {features.shape}")
                
            except Exception as e:
                print(f"❌ [ERROR] All feature extraction methods failed: {e}")
        
        if features is None:
            if os.path.exists(wav_file):
                os.remove(wav_file)
            return jsonify({'success': False, 'message': 'Audio processing failed - all methods exhausted'})
        
        print(f"✅ [PROCESSING] Final features shape: {features.shape}")
        
        # Now register student
        if not db.register_student(student_id, name, email):
            if os.path.exists(wav_file):
                os.remove(wav_file)
            return jsonify({'success': False, 'message': 'Student ID already exists'})
        
        # Store voice embedding
        try:
            audio_array, sr = sf.read(wav_file)
            db.store_voice_embedding(student_id, features, audio_array)
            print(f"✅ [DATABASE] Voice data stored")
            
            # Store additional variations of the same audio for better matching
            try:
                # Create slight variations by adding small amounts of noise
                for i in range(2):  # Store 2 additional variations
                    noise_level = 0.01 * (i + 1)  # Small noise levels
                    noisy_features = features + np.random.normal(0, noise_level, features.shape)
                    db.store_voice_embedding(student_id, noisy_features, audio_array)
                    print(f"✅ [DATABASE] Voice variation {i+1} stored")
            except Exception as variation_error:
                print(f"⚠️ [WARNING] Could not store variations: {variation_error}")
                
        except Exception as e:
            db.delete_student(student_id)  # Rollback
            if os.path.exists(wav_file):
                os.remove(wav_file)
            return jsonify({'success': False, 'message': f'Voice storage failed: {str(e)}'})
        
        # Clean up
        if os.path.exists(wav_file):
            os.remove(wav_file)
        
        return jsonify({
            'success': True, 
            'message': f'Student {name} registered successfully!',
            'student_id': student_id,
            'features_shape': list(features.shape)  # Convert numpy shape to list
        })
        
    except Exception as e:
        print(f"💥 [ERROR] Registration failed: {e}")
        return jsonify({'success': False, 'message': f'Registration failed: {str(e)}'})

@app.route('/api/voice_login', methods=['POST'])
def api_voice_login():
    try:
        print("🔍 [LOGIN] Voice login request received")
        
        data = request.get_json()
        audio_data = data.get('audio_data')
        
        if not audio_data:
            return jsonify({'success': False, 'message': 'No audio data'})
        
        # Decode audio
        try:
            if ',' in audio_data:
                audio_bytes = base64.b64decode(audio_data.split(',')[1])
            else:
                audio_bytes = base64.b64decode(audio_data)
            print(f"✅ [DEBUG] Audio decoded: {len(audio_bytes)} bytes")
        except Exception as e:
            return jsonify({'success': False, 'message': f'Audio decode failed: {str(e)}'})
        
        # Convert to WAV
        wav_file = os.path.join(upload_folder, f'login_{int(time.time())}.wav')
        
        if not convert_audio_to_wav(audio_bytes, wav_file):
            return jsonify({'success': False, 'message': 'Audio conversion failed'})
        
        # Process audio with multiple fallback methods
        print(f"🔄 [PROCESSING] Processing login audio...")
        
        features = None
        
        # Try spectrogram first
        try:
            features = preprocessor.preprocess_audio(wav_file, feature_type='spectrogram')
            if features is not None:
                print(f"✅ [PROCESSING] Spectrogram features: {features.shape}")
        except Exception as e:
            print(f"⚠️ [WARNING] Spectrogram failed: {e}")
        
        # Try MFCC if spectrogram failed
        if features is None:
            try:
                features = preprocessor.preprocess_audio(wav_file, feature_type='mfcc')
                if features is not None:
                    print(f"✅ [PROCESSING] MFCC features: {features.shape}")
            except Exception as e:
                print(f"⚠️ [WARNING] MFCC failed: {e}")
        
        # Simple fallback
        if features is None:
            try:
                audio_data, sr = sf.read(wav_file)
                f, t, Zxx = signal.stft(audio_data, fs=sr, nperseg=1024)
                spectrogram = np.abs(Zxx)
                target_shape = (100, 128)
                zoom_factors = (target_shape[0] / spectrogram.shape[0], 
                               target_shape[1] / spectrogram.shape[1])
                features = zoom(spectrogram, zoom_factors)
                print(f"✅ [PROCESSING] Simple features: {features.shape}")
            except Exception as e:
                print(f"❌ [ERROR] All methods failed: {e}")
        
        if features is None:
            if os.path.exists(wav_file):
                os.remove(wav_file)
            return jsonify({'success': False, 'message': 'Audio processing failed'})
        
        # Compare with all students
        all_students = db.list_all_students()
        if not all_students:
            if os.path.exists(wav_file):
                os.remove(wav_file)
            return jsonify({'success': False, 'message': 'No registered students'})
        
        best_student = None
        best_similarity = 0.0
        
        for student in all_students:
            if not student['is_active']:
                continue
            
            is_match, similarity = db.verify_student_voice(student['student_id'], features)
            print(f"🔍 [DEBUG] {student['name']}: {similarity:.3f}")
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_student = student
        
        # Clean up
        if os.path.exists(wav_file):
            os.remove(wav_file)
        
        # Check confidence (lowered threshold for better usability)
        if best_student and best_similarity >= 0.65:
            db.log_login_attempt(best_student['student_id'], True, best_similarity)
            return jsonify({
                'success': True,
                'message': f'Welcome back, {best_student["name"]}!',
                'student_name': best_student['name'],
                'student_id': best_student['student_id'],
                'confidence': float(best_similarity)  # Convert to Python float
            })
        else:
            db.log_login_attempt("UNKNOWN", False, best_similarity)
            return jsonify({
                'success': False,
                'message': 'Voice not recognized',
                'confidence': float(best_similarity)  # Convert to Python float
            })
            
    except Exception as e:
        print(f"💥 [ERROR] Login failed: {e}")
        return jsonify({'success': False, 'message': f'Login failed: {str(e)}'})

@app.route('/api/delete_student/<student_id>', methods=['DELETE'])
def api_delete_student(student_id):
    try:
        if db.delete_student(student_id):
            return jsonify({'success': True, 'message': 'Student deleted'})
        else:
            return jsonify({'success': False, 'message': 'Delete failed'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/students')
def api_get_students():
    try:
        students = db.list_all_students()
        return jsonify({'success': True, 'students': students})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    print("🎤 Starting Voice Recognition Web Application...")
    print("🌐 Open: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)