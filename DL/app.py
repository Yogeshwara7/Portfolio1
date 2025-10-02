import os
import sys
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from datetime import datetime

from preprocessing import AudioPreprocessor
from model import VoiceRecognitionCNN
from database import VoiceDatabase
from audio_recorder import AudioRecorder

class VoiceRecognitionApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Student Voice Recognition Login System")
        self.root.geometry("800x600")
        
        # Initialize components
        self.preprocessor = AudioPreprocessor()
        self.db = VoiceDatabase()
        self.recorder = AudioRecorder()
        self.model = None
        
        # Variables
        self.current_audio = None
        self.is_recording = False
        
        # Create GUI
        self.create_gui()
        
        # Load existing model if available
        self.load_model()
    
    def create_gui(self):
        """Create the main GUI interface"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Registration tab
        self.create_registration_tab(notebook)
        
        # Login tab
        self.create_login_tab(notebook)
        
        # Management tab
        self.create_management_tab(notebook)
        
        # Training tab
        self.create_training_tab(notebook)
    
    def create_registration_tab(self, notebook):
        """Create student registration tab"""
        reg_frame = ttk.Frame(notebook)
        notebook.add(reg_frame, text="Register Student")
        
        # Student information
        info_frame = ttk.LabelFrame(reg_frame, text="Student Information", padding=10)
        info_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(info_frame, text="Student ID:").grid(row=0, column=0, sticky='w', pady=2)
        self.reg_student_id = ttk.Entry(info_frame, width=30)
        self.reg_student_id.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(info_frame, text="Name:").grid(row=1, column=0, sticky='w', pady=2)
        self.reg_name = ttk.Entry(info_frame, width=30)
        self.reg_name.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(info_frame, text="Email:").grid(row=2, column=0, sticky='w', pady=2)
        self.reg_email = ttk.Entry(info_frame, width=30)
        self.reg_email.grid(row=2, column=1, padx=5, pady=2)
        
        # Voice recording
        voice_frame = ttk.LabelFrame(reg_frame, text="Voice Registration", padding=10)
        voice_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        ttk.Label(voice_frame, text="Please record your voice saying: 'Login My Account'").pack(pady=5)
        
        button_frame = ttk.Frame(voice_frame)
        button_frame.pack(pady=10)
        
        self.reg_record_btn = ttk.Button(button_frame, text="Record Voice", command=self.record_registration_voice)
        self.reg_record_btn.pack(side='left', padx=5)
        
        self.reg_play_btn = ttk.Button(button_frame, text="Play Recording", command=self.play_recorded_audio, state='disabled')
        self.reg_play_btn.pack(side='left', padx=5)
        
        self.reg_register_btn = ttk.Button(button_frame, text="Register Student", command=self.register_student, state='disabled')
        self.reg_register_btn.pack(side='left', padx=5)
        
        # Status
        self.reg_status = ttk.Label(voice_frame, text="Ready to record", foreground='blue')
        self.reg_status.pack(pady=5)
    
    def create_login_tab(self, notebook):
        """Create login tab"""
        login_frame = ttk.Frame(notebook)
        notebook.add(login_frame, text="Voice Login")
        
        # Login interface
        login_main = ttk.LabelFrame(login_frame, text="Voice Authentication", padding=30)
        login_main.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Welcome message
        welcome_label = ttk.Label(login_main, text="🎤 Voice Authentication System", 
                                font=('Arial', 16, 'bold'), foreground='navy')
        welcome_label.pack(pady=10)
        
        instruction_label = ttk.Label(login_main, text="Simply speak to login - no typing required!", 
                                    font=('Arial', 12), foreground='gray')
        instruction_label.pack(pady=5)
        
        # Voice prompt
        prompt_frame = ttk.Frame(login_main)
        prompt_frame.pack(pady=20)
        
        ttk.Label(prompt_frame, text="Please speak clearly:", 
                 font=('Arial', 12)).pack()
        ttk.Label(prompt_frame, text="'Login My Account'", 
                 font=('Arial', 14, 'bold'), foreground='darkgreen').pack(pady=5)
        
        # Record button
        self.login_record_btn = ttk.Button(login_main, text="🎤 Start Voice Login", 
                                         command=self.record_login_voice, 
                                         style='Accent.TButton')
        self.login_record_btn.pack(pady=20)
        
        self.login_status = ttk.Label(login_main, text="Ready for voice authentication", 
                                    foreground='blue', font=('Arial', 11))
        self.login_status.pack(pady=10)
        
        # Login result
        self.login_result_frame = ttk.Frame(login_main)
        self.login_result_frame.pack(pady=20)
    
    def create_management_tab(self, notebook):
        """Create student management tab"""
        mgmt_frame = ttk.Frame(notebook)
        notebook.add(mgmt_frame, text="Manage Students")
        
        # Student list
        list_frame = ttk.LabelFrame(mgmt_frame, text="Registered Students", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview for student list
        columns = ('ID', 'Name', 'Email', 'Registration Date', 'Status')
        self.student_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=scrollbar.set)
        
        self.student_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Management buttons
        btn_frame = ttk.Frame(mgmt_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Refresh List", command=self.refresh_student_list).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected_student).pack(side='left', padx=5)
        
        # Load initial student list
        self.refresh_student_list()
    
    def create_training_tab(self, notebook):
        """Create model training tab"""
        train_frame = ttk.Frame(notebook)
        notebook.add(train_frame, text="Train Model")
        
        # Training controls
        control_frame = ttk.LabelFrame(train_frame, text="Model Training", padding=10)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(control_frame, text="Train the CNN model with registered voice data").pack(pady=5)
        
        self.train_btn = ttk.Button(control_frame, text="Train Model", command=self.train_model)
        self.train_btn.pack(pady=10)
        
        # Training progress
        self.train_progress = ttk.Progressbar(control_frame, mode='indeterminate')
        self.train_progress.pack(fill='x', pady=5)
        
        # Training status
        self.train_status = ttk.Label(control_frame, text="Ready to train", foreground='blue')
        self.train_status.pack(pady=5)
        
        # Model info
        info_frame = ttk.LabelFrame(train_frame, text="Model Information", padding=10)
        info_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.model_info = tk.Text(info_frame, height=15, width=70)
        self.model_info.pack(fill='both', expand=True)
        
        # Update model info
        self.update_model_info()
    
    def record_registration_voice(self):
        """Record voice for student registration"""
        if not self.reg_student_id.get() or not self.reg_name.get():
            messagebox.showerror("Error", "Please enter Student ID and Name first")
            return
        
        def record_thread():
            try:
                self.reg_status.config(text="Recording... Speak now!", foreground='red')
                self.reg_record_btn.config(state='disabled')
                
                # Record audio
                self.current_audio = self.recorder.record_audio(duration=5)
                
                self.reg_status.config(text="Recording completed!", foreground='green')
                self.reg_play_btn.config(state='normal')
                self.reg_register_btn.config(state='normal')
                self.reg_record_btn.config(state='normal')
                
            except Exception as e:
                self.reg_status.config(text=f"Recording failed: {str(e)}", foreground='red')
                self.reg_record_btn.config(state='normal')
        
        threading.Thread(target=record_thread, daemon=True).start()
    
    def play_recorded_audio(self):
        """Play the recorded audio"""
        if self.current_audio is not None:
            threading.Thread(target=lambda: self.recorder.play_audio(self.current_audio), daemon=True).start()
    
    def register_student(self):
        """Register student with voice data"""
        student_id = self.reg_student_id.get()
        name = self.reg_name.get()
        email = self.reg_email.get()
        
        if not student_id or not name or self.current_audio is None:
            messagebox.showerror("Error", "Please fill all required fields and record voice")
            return
        
        try:
            # Register student in database
            if self.db.register_student(student_id, name, email):
                
                # Process audio and extract features
                temp_audio_file = f"temp_{student_id}.wav"
                self.recorder.save_audio(self.current_audio, temp_audio_file)
                
                # Extract features
                features = self.preprocessor.preprocess_audio(temp_audio_file, feature_type='spectrogram')
                
                if features is not None:
                    # Store voice embedding (using raw features for now)
                    self.db.store_voice_embedding(student_id, features, self.current_audio)
                    
                    messagebox.showinfo("Success", f"Student {name} registered successfully!")
                    
                    # Clear form
                    self.reg_student_id.delete(0, tk.END)
                    self.reg_name.delete(0, tk.END)
                    self.reg_email.delete(0, tk.END)
                    self.current_audio = None
                    self.reg_play_btn.config(state='disabled')
                    self.reg_register_btn.config(state='disabled')
                    self.reg_status.config(text="Ready to record", foreground='blue')
                    
                    # Refresh student list
                    self.refresh_student_list()
                else:
                    messagebox.showerror("Error", "Failed to process audio")
                
                # Clean up temp file
                if os.path.exists(temp_audio_file):
                    os.remove(temp_audio_file)
            
        except Exception as e:
            messagebox.showerror("Error", f"Registration failed: {str(e)}")
    
    def record_login_voice(self):
        """Record voice for login attempt - identifies speaker automatically"""
        def login_thread():
            try:
                self.login_status.config(text="🔴 Recording... Speak now!", foreground='red')
                self.login_record_btn.config(state='disabled')
                
                # Record audio
                login_audio = self.recorder.record_audio(duration=5)
                
                # Process and identify speaker
                self.identify_and_login(login_audio)
                
            except Exception as e:
                self.login_status.config(text=f"Login failed: {str(e)}", foreground='red')
            finally:
                self.login_record_btn.config(state='normal')
        
        threading.Thread(target=login_thread, daemon=True).start()
    
    def identify_and_login(self, audio_data):
        """Identify speaker from voice and login automatically"""
        try:
            self.login_status.config(text="🔍 Processing voice... Identifying speaker", foreground='orange')
            
            # Process audio
            temp_audio_file = f"temp_login_{int(time.time())}.wav"
            self.recorder.save_audio(audio_data, temp_audio_file)
            
            # Extract features
            features = self.preprocessor.preprocess_audio(temp_audio_file, feature_type='spectrogram')
            
            if features is None:
                self.show_login_result(False, "Failed to process audio", 0.0)
                return
            
            # Get all registered students
            all_students = self.db.list_all_students()
            if not all_students:
                self.show_login_result(False, "No registered students found", 0.0)
                return
            
            best_match = None
            best_similarity = 0.0
            best_student = None
            
            # If model is trained, use it for identification
            if self.model and self.model.model:
                # Reshape features for CNN input
                features_reshaped = features.reshape(1, features.shape[0], features.shape[1], 1)
                
                # Get prediction
                predicted_class, confidence, is_confident = self.model.predict_speaker(features_reshaped)
                
                if is_confident and confidence > 0.7:
                    # Map predicted class back to student (this requires storing class mapping)
                    # For now, we'll fall back to similarity matching
                    pass
            
            # Use similarity matching to identify speaker
            self.login_status.config(text="🔍 Comparing with registered voices...", foreground='orange')
            
            for student in all_students:
                if not student['is_active']:
                    continue
                    
                student_id = student['student_id']
                is_match, similarity = self.db.verify_student_voice(student_id, features)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_student = student
                    best_match = is_match
            
            # Determine if we have a confident match
            confidence_threshold = 0.75  # Adjust as needed
            
            if best_student and best_similarity >= confidence_threshold:
                # Successful identification and login
                self.show_login_result(True, f"Welcome back, {best_student['name']}!", best_similarity)
                
                # Log successful attempt
                self.db.log_login_attempt(best_student['student_id'], True, best_similarity)
                
            elif best_student and best_similarity >= 0.5:
                # Possible match but low confidence
                self.show_login_result(False, 
                    f"Possible match: {best_student['name']} (Low confidence)", 
                    best_similarity)
                
                # Log failed attempt
                self.db.log_login_attempt(best_student['student_id'], False, best_similarity)
                
            else:
                # No match found
                self.show_login_result(False, "Voice not recognized - Please register first", best_similarity)
                
                # Log failed attempt with unknown user
                self.db.log_login_attempt("UNKNOWN", False, best_similarity)
            
            # Clean up
            if os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)
                
        except Exception as e:
            self.show_login_result(False, f"Authentication error: {str(e)}", 0.0)
    
    def show_login_result(self, success, message, confidence):
        """Display login result"""
        # Clear previous result
        for widget in self.login_result_frame.winfo_children():
            widget.destroy()
        
        if success:
            color = 'green'
            icon = "✓"
        else:
            color = 'red'
            icon = "✗"
        
        result_label = ttk.Label(self.login_result_frame, 
                               text=f"{icon} {message}", 
                               foreground=color, 
                               font=('Arial', 14, 'bold'))
        result_label.pack(pady=5)
        
        confidence_label = ttk.Label(self.login_result_frame, 
                                   text=f"Confidence: {confidence:.2%}", 
                                   foreground='blue')
        confidence_label.pack()
        
        self.login_status.config(text="Login attempt completed", foreground='blue')
    
    def refresh_student_list(self):
        """Refresh the student list in management tab"""
        # Clear existing items
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        # Get all students
        students = self.db.list_all_students()
        
        for student in students:
            status = "Active" if student['is_active'] else "Inactive"
            self.student_tree.insert('', 'end', values=(
                student['student_id'],
                student['name'],
                student['email'] or 'N/A',
                student['registration_date'],
                status
            ))
    
    def delete_selected_student(self):
        """Delete selected student"""
        selection = self.student_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a student to delete")
            return
        
        item = self.student_tree.item(selection[0])
        student_id = item['values'][0]
        student_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete student {student_name} ({student_id})?\n"
                              "This will remove all their voice data."):
            if self.db.delete_student(student_id):
                messagebox.showinfo("Success", "Student deleted successfully")
                self.refresh_student_list()
    
    def train_model(self):
        """Train the CNN model with registered voice data"""
        def training_thread():
            try:
                self.train_status.config(text="Preparing training data...", foreground='blue')
                self.train_progress.start()
                self.train_btn.config(state='disabled')
                
                # Get all student embeddings
                student_data = self.db.get_all_student_embeddings()
                
                if len(student_data) < 2:
                    self.train_status.config(text="Need at least 2 students to train model", foreground='red')
                    return
                
                # Prepare training data
                X_train = []
                y_train = []
                student_ids = list(student_data.keys())
                
                for i, (student_id, data) in enumerate(student_data.items()):
                    for embedding in data['embeddings']:
                        X_train.append(embedding)
                        y_train.append(i)  # Use index as class label
                
                X_train = np.array(X_train)
                y_train = np.array(y_train)
                
                # Reshape for CNN (add channel dimension)
                X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], X_train.shape[2], 1)
                
                self.train_status.config(text="Training CNN model...", foreground='blue')
                
                # Create and train model
                input_shape = X_train.shape[1:]
                num_classes = len(student_ids)
                
                self.model = VoiceRecognitionCNN(input_shape, num_classes)
                self.model.build_model()
                self.model.compile_model()
                
                # Train model
                history = self.model.train_model(X_train, y_train, epochs=30, batch_size=16)
                
                # Save model
                self.model.save_model()
                
                self.train_status.config(text="Model trained successfully!", foreground='green')
                self.update_model_info()
                
            except Exception as e:
                self.train_status.config(text=f"Training failed: {str(e)}", foreground='red')
            finally:
                self.train_progress.stop()
                self.train_btn.config(state='normal')
        
        threading.Thread(target=training_thread, daemon=True).start()
    
    def load_model(self):
        """Load existing trained model"""
        try:
            if os.path.exists('voice_recognition_model.h5'):
                # We need to know the input shape and number of classes
                # For now, we'll create a placeholder model
                self.model = VoiceRecognitionCNN((100, 128, 1), 10)  # Placeholder values
                if self.model.load_model():
                    self.update_model_info()
        except Exception as e:
            print(f"Could not load existing model: {e}")
    
    def update_model_info(self):
        """Update model information display"""
        self.model_info.delete(1.0, tk.END)
        
        info_text = "Voice Recognition Model Information\n"
        info_text += "=" * 40 + "\n\n"
        
        if self.model and self.model.model:
            info_text += "Model Status: Loaded\n"
            info_text += f"Model Architecture: CNN\n"
            info_text += f"Input Shape: {self.model.input_shape}\n"
            info_text += f"Number of Classes: {self.model.num_classes}\n\n"
            
            # Model summary
            info_text += "Model Summary:\n"
            info_text += "-" * 20 + "\n"
            
            # Get model summary as string
            import io
            import contextlib
            
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                self.model.model.summary()
            model_summary = f.getvalue()
            info_text += model_summary
        else:
            info_text += "Model Status: Not loaded\n"
            info_text += "Please train a model using registered voice data.\n"
        
        self.model_info.insert(1.0, info_text)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = VoiceRecognitionApp()
    app.run()