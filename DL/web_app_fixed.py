from flask import Flask, render_template, request, jsonify
import os
import base64
import numpy as np
import soundfile as sf
import librosa
import time

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
        
        # Save raw audio first
        temp_raw = output_path + '.raw'
        with open(temp_raw, 'wb') as f:
            f.write(audio_bytes)
        
        # Try to load with librosa
        try:
            audio_data, sr = librosa.load(temp_raw, sr=22050)
            print(f"✅ [CONVERSION] Librosa loaded: shape={audio_data.shape}, sr={sr}")
            
            # Save as WAV
            sf.write(output_path, audio_data, sr)
            print(f"✅ [CONVERSION] Saved as WAV: {output_path}")
            
            # Clean up raw file
            if os.path.exists(temp_raw):
                os.remove(temp_raw)
            
            return True
            
        except Exception as e:
            print(f"⚠️ [WARNING] Librosa failed: {e}")
            
            # Try direct WAV save (assume it's already WAV-like)
            try:
                # Just rename the file and hope for the best
                os.rename(temp_raw, output_path)
                print(f"✅ [CONVERSION] Used raw file as WAV")
                return True
            except Exception as e2:
                print(f"❌ [ERROR] Raw file conversion failed: {e2}")
                if os.path.exists(temp_raw):
                    os.remove(temp_raw)
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
        features = preprocessor.preprocess_audio(wav_file, feature_type='spectrogram')
        
        if features is None:
            if os.path.exists(wav_file):
                os.remove(wav_file)
            return jsonify({'success': False, 'message': 'Audio processing failed - check audio quality'})
        
        print(f"✅ [PROCESSING] Features extracted: {features.shape}")
        
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
        except Exception as e:
            db.delete_student(student_id)  # Rollback
            if os.path.exists(wav_file):
                os.remove(wav_file)
            return jsonify({'success': False, 'message': f'Voice storage failed: {str(e)}'})
        
        # Clean up
        if os.path.exists(wav_file):
            os.remove(wav_file)
        
        return jsonify({'success': True, 'message': f'Student {name} registered successfully!'})
        
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
        
        # Process audio
        features = preprocessor.preprocess_audio(wav_file, feature_type='spectrogram')
        
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
        
        # Check confidence
        if best_student and best_similarity >= 0.75:
            db.log_login_attempt(best_student['student_id'], True, best_similarity)
            return jsonify({
                'success': True,
                'message': f'Welcome back, {best_student["name"]}!',
                'student_name': best_student['name'],
                'student_id': best_student['student_id'],
                'confidence': best_similarity
            })
        else:
            db.log_login_attempt("UNKNOWN", False, best_similarity)
            return jsonify({
                'success': False,
                'message': 'Voice not recognized',
                'confidence': best_similarity
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