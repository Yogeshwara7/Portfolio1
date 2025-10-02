#!/usr/bin/env python3
"""
Command Line Interface for Student Voice Recognition Login System
"""

import os
import sys
import argparse
import numpy as np
from datetime import datetime

from preprocessing import AudioPreprocessor
from model import VoiceRecognitionCNN
from database import VoiceDatabase
from audio_recorder import AudioRecorder

class VoiceRecognitionCLI:
    def __init__(self):
        self.preprocessor = AudioPreprocessor()
        self.db = VoiceDatabase()
        self.recorder = AudioRecorder()
        self.model = None
        
        # Load existing model if available
        self.load_model()
    
    def register_student(self, student_id, name, email=None):
        """Register a new student with voice recording"""
        print(f"\n=== Registering Student: {name} ===")
        print(f"Student ID: {student_id}")
        
        # Register student in database
        if not self.db.register_student(student_id, name, email):
            print("❌ Student registration failed - ID already exists")
            return False
        
        print("✅ Student registered in database")
        
        # Record voice
        print("\n🎤 Voice Recording")
        print("Please say: 'Login My Account'")
        input("Press Enter when ready to record...")
        
        try:
            # Record audio
            audio_data = self.recorder.record_audio(duration=5)
            
            # Save temporary file
            temp_file = f"temp_{student_id}.wav"
            self.recorder.save_audio(audio_data, temp_file)
            
            # Process audio
            features = self.preprocessor.preprocess_audio(temp_file, feature_type='spectrogram')
            
            if features is not None:
                # Store voice embedding
                self.db.store_voice_embedding(student_id, features, audio_data)
                print("✅ Voice data stored successfully")
                
                # Clean up
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                
                return True
            else:
                print("❌ Failed to process audio")
                return False
                
        except Exception as e:
            print(f"❌ Recording failed: {e}")
            return False
    
    def login_student(self, student_id=None):
        """Attempt to login student using voice recognition"""
        if student_id:
            # Traditional login with known ID
            print(f"\n=== Login Attempt: {student_id} ===")
            
            # Check if student exists
            student_info = self.db.get_student_info(student_id)
            if not student_info:
                print("❌ Student not found")
                return False
            
            print(f"Student: {student_info['name']}")
            return self._verify_specific_student(student_id)
        else:
            # Voice-only identification and login
            return self._voice_only_login()
    
    def _verify_specific_student(self, student_id):
        """Verify a specific student's voice"""
        print("\n🎤 Voice Authentication")
        print("Please say: 'Login My Account'")
        input("Press Enter when ready to record...")
        
        try:
            # Record audio
            audio_data = self.recorder.record_audio(duration=5)
            
            # Save temporary file
            temp_file = f"temp_login_{student_id}.wav"
            self.recorder.save_audio(audio_data, temp_file)
            
            # Process audio
            features = self.preprocessor.preprocess_audio(temp_file, feature_type='spectrogram')
            
            if features is None:
                print("❌ Failed to process audio")
                return False
            
            # Get student info
            student_info = self.db.get_student_info(student_id)
            
            # Verify using similarity
            is_match, similarity = self.db.verify_student_voice(student_id, features)
            
            if is_match:
                print(f"✅ Login Successful!")
                print(f"Welcome {student_info['name']}!")
                print(f"Similarity: {similarity:.2%}")
                success = True
            else:
                print(f"❌ Login Failed - Voice not recognized")
                print(f"Similarity: {similarity:.2%}")
                success = False
            
            # Log attempt
            self.db.log_login_attempt(student_id, success, similarity)
            
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            return success
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    def _voice_only_login(self):
        """Voice-only identification and login"""
        print("\n=== 🎤 Voice-Only Authentication ===")
        print("No typing required - just speak to login!")
        print("\nPlease say: 'Login My Account'")
        input("Press Enter when ready to record...")
        
        try:
            # Record audio
            audio_data = self.recorder.record_audio(duration=5)
            
            # Save temporary file
            temp_file = f"temp_voice_login_{int(time.time())}.wav"
            self.recorder.save_audio(audio_data, temp_file)
            
            # Process audio
            features = self.preprocessor.preprocess_audio(temp_file, feature_type='spectrogram')
            
            if features is None:
                print("❌ Failed to process audio")
                return False
            
            print("🔍 Identifying speaker...")
            
            # Get all registered students
            all_students = self.db.list_all_students()
            if not all_students:
                print("❌ No registered students found")
                return False
            
            best_match = None
            best_similarity = 0.0
            best_student = None
            
            # Compare with all registered voices
            for student in all_students:
                if not student['is_active']:
                    continue
                    
                student_id = student['student_id']
                is_match, similarity = self.db.verify_student_voice(student_id, features)
                
                print(f"  Checking {student['name']}: {similarity:.2%}")
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_student = student
                    best_match = is_match
            
            # Determine if we have a confident match
            confidence_threshold = 0.75
            
            if best_student and best_similarity >= confidence_threshold:
                print(f"\n✅ Login Successful!")
                print(f"Welcome back, {best_student['name']}!")
                print(f"Voice Match: {best_similarity:.2%}")
                
                # Log successful attempt
                self.db.log_login_attempt(best_student['student_id'], True, best_similarity)
                success = True
                
            elif best_student and best_similarity >= 0.5:
                print(f"\n⚠️  Possible Match: {best_student['name']}")
                print(f"Voice Similarity: {best_similarity:.2%}")
                print("❌ Confidence too low for login")
                
                # Log failed attempt
                self.db.log_login_attempt(best_student['student_id'], False, best_similarity)
                success = False
                
            else:
                print(f"\n❌ Voice Not Recognized")
                print(f"Best match: {best_similarity:.2%}")
                print("Please register your voice first")
                
                # Log failed attempt
                self.db.log_login_attempt("UNKNOWN", False, best_similarity)
                success = False
            
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            return success
            
        except Exception as e:
            print(f"❌ Voice authentication failed: {e}")
            return False
    
    def train_model(self):
        """Train the CNN model with registered voice data"""
        print("\n=== Training Voice Recognition Model ===")
        
        # Get all student embeddings
        student_data = self.db.get_all_student_embeddings()
        
        if len(student_data) < 2:
            print("❌ Need at least 2 registered students to train model")
            return False
        
        print(f"Found {len(student_data)} students with voice data")
        
        try:
            # Prepare training data
            X_train = []
            y_train = []
            student_ids = list(student_data.keys())
            
            print("Preparing training data...")
            for i, (student_id, data) in enumerate(student_data.items()):
                print(f"  - {data['name']}: {len(data['embeddings'])} samples")
                for embedding in data['embeddings']:
                    X_train.append(embedding)
                    y_train.append(i)
            
            X_train = np.array(X_train)
            y_train = np.array(y_train)
            
            # Reshape for CNN
            X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], X_train.shape[2], 1)
            
            print(f"Training data shape: {X_train.shape}")
            print(f"Number of classes: {len(student_ids)}")
            
            # Create and train model
            input_shape = X_train.shape[1:]
            num_classes = len(student_ids)
            
            self.model = VoiceRecognitionCNN(input_shape, num_classes)
            self.model.build_model()
            self.model.compile_model()
            
            print("\nTraining model...")
            history = self.model.train_model(X_train, y_train, epochs=30, batch_size=16)
            
            # Save model
            self.model.save_model()
            
            print("✅ Model trained and saved successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Training failed: {e}")
            return False
    
    def list_students(self):
        """List all registered students"""
        print("\n=== Registered Students ===")
        
        students = self.db.list_all_students()
        
        if not students:
            print("No students registered")
            return
        
        print(f"{'ID':<15} {'Name':<20} {'Email':<25} {'Registration Date':<20} {'Status'}")
        print("-" * 90)
        
        for student in students:
            status = "Active" if student['is_active'] else "Inactive"
            email = student['email'] or 'N/A'
            reg_date = student['registration_date'][:19]  # Remove microseconds
            
            print(f"{student['student_id']:<15} {student['name']:<20} {email:<25} {reg_date:<20} {status}")
    
    def delete_student(self, student_id):
        """Delete a student and their voice data"""
        print(f"\n=== Deleting Student: {student_id} ===")
        
        # Check if student exists
        student_info = self.db.get_student_info(student_id)
        if not student_info:
            print("❌ Student not found")
            return False
        
        print(f"Student: {student_info['name']}")
        
        # Confirm deletion
        confirm = input("Are you sure you want to delete this student? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Deletion cancelled")
            return False
        
        if self.db.delete_student(student_id):
            print("✅ Student deleted successfully")
            return True
        else:
            print("❌ Failed to delete student")
            return False
    
    def load_model(self):
        """Load existing trained model"""
        try:
            if os.path.exists('voice_recognition_model.h5'):
                # Create placeholder model (we need to determine actual shape from data)
                self.model = VoiceRecognitionCNN((100, 128, 1), 10)
                if self.model.load_model():
                    print("✅ Existing model loaded")
                    return True
        except Exception as e:
            print(f"Could not load existing model: {e}")
        return False
    
    def show_model_info(self):
        """Show information about the current model"""
        print("\n=== Model Information ===")
        
        if self.model and self.model.model:
            print("Model Status: Loaded")
            print(f"Input Shape: {self.model.input_shape}")
            print(f"Number of Classes: {self.model.num_classes}")
            print("\nModel Architecture:")
            self.model.model.summary()
        else:
            print("Model Status: Not loaded")
            print("Train a model using the --train option")

def main():
    parser = argparse.ArgumentParser(description="Student Voice Recognition Login System")
    parser.add_argument('--register', nargs='+', help='Register student: --register STUDENT_ID NAME [EMAIL]')
    parser.add_argument('--login', nargs='?', const='', help='Login student: --login [STUDENT_ID] (omit ID for voice-only login)')
    parser.add_argument('--train', action='store_true', help='Train the CNN model')
    parser.add_argument('--list', action='store_true', help='List all registered students')
    parser.add_argument('--delete', help='Delete student: --delete STUDENT_ID')
    parser.add_argument('--model-info', action='store_true', help='Show model information')
    parser.add_argument('--devices', action='store_true', help='List audio devices')
    
    args = parser.parse_args()
    
    cli = VoiceRecognitionCLI()
    
    if args.devices:
        cli.recorder.list_audio_devices()
    elif args.register:
        if len(args.register) < 2:
            print("❌ Usage: --register STUDENT_ID NAME [EMAIL]")
            sys.exit(1)
        
        student_id = args.register[0]
        name = args.register[1]
        email = args.register[2] if len(args.register) > 2 else None
        
        cli.register_student(student_id, name, email)
    
    elif args.login is not None:
        if args.login:
            cli.login_student(args.login)  # Login with specific ID
        else:
            cli.login_student()  # Voice-only login
    
    elif args.train:
        cli.train_model()
    
    elif args.list:
        cli.list_students()
    
    elif args.delete:
        cli.delete_student(args.delete)
    
    elif args.model_info:
        cli.show_model_info()
    
    else:
        # Interactive mode
        print("🎤 Student Voice Recognition Login System")
        print("=" * 45)
        
        while True:
            print("\nOptions:")
            print("1. Register Student")
            print("2. Login Student")
            print("3. Train Model")
            print("4. List Students")
            print("5. Delete Student")
            print("6. Model Info")
            print("7. Exit")
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == '1':
                student_id = input("Enter Student ID: ").strip()
                name = input("Enter Name: ").strip()
                email = input("Enter Email (optional): ").strip() or None
                cli.register_student(student_id, name, email)
            
            elif choice == '2':
                print("\nLogin Options:")
                print("1. Voice-only login (recommended)")
                print("2. Login with Student ID")
                
                login_choice = input("Choose login method (1-2): ").strip()
                
                if login_choice == '1':
                    cli.login_student()  # Voice-only
                elif login_choice == '2':
                    student_id = input("Enter Student ID: ").strip()
                    cli.login_student(student_id)  # With ID
                else:
                    print("❌ Invalid choice")
            
            elif choice == '3':
                cli.train_model()
            
            elif choice == '4':
                cli.list_students()
            
            elif choice == '5':
                student_id = input("Enter Student ID to delete: ").strip()
                cli.delete_student(student_id)
            
            elif choice == '6':
                cli.show_model_info()
            
            elif choice == '7':
                print("Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()