import sqlite3
import pickle
import numpy as np
import hashlib
import os
from datetime import datetime

class VoiceDatabase:
    def __init__(self, db_path='voice_recognition.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create voice_embeddings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                embedding_data BLOB NOT NULL,
                audio_hash TEXT NOT NULL,
                confidence_score REAL,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (student_id)
            )
        ''')
        
        # Create login_attempts table for security tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN NOT NULL,
                confidence_score REAL,
                ip_address TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_student(self, student_id, name, email=None):
        """Register a new student"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO students (student_id, name, email)
                VALUES (?, ?, ?)
            ''', (student_id, name, email))
            
            conn.commit()
            print(f"Student {name} registered successfully with ID: {student_id}")
            return True
            
        except sqlite3.IntegrityError:
            print(f"Student with ID {student_id} already exists")
            return False
        finally:
            conn.close()
    
    def store_voice_embedding(self, student_id, embedding, audio_data=None, confidence_score=None):
        """Store voice embedding for a student"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if student exists
        cursor.execute('SELECT id FROM students WHERE student_id = ?', (student_id,))
        if not cursor.fetchone():
            conn.close()
            raise ValueError(f"Student with ID {student_id} not found")
        
        # Create hash of audio data for integrity
        audio_hash = None
        if audio_data is not None:
            audio_hash = hashlib.md5(audio_data.tobytes()).hexdigest()
        
        # Serialize embedding
        embedding_blob = pickle.dumps(embedding)
        
        try:
            cursor.execute('''
                INSERT INTO voice_embeddings (student_id, embedding_data, audio_hash, confidence_score)
                VALUES (?, ?, ?, ?)
            ''', (student_id, embedding_blob, audio_hash, confidence_score))
            
            conn.commit()
            print(f"Voice embedding stored for student {student_id}")
            return True
            
        except Exception as e:
            print(f"Error storing voice embedding: {e}")
            return False
        finally:
            conn.close()
    
    def get_student_embeddings(self, student_id):
        """Retrieve all voice embeddings for a student"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT embedding_data, confidence_score, registration_date
            FROM voice_embeddings
            WHERE student_id = ?
            ORDER BY registration_date DESC
        ''', (student_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        embeddings = []
        for row in results:
            embedding = pickle.loads(row[0])
            embeddings.append({
                'embedding': embedding,
                'confidence_score': row[1],
                'registration_date': row[2]
            })
        
        return embeddings
    
    def get_all_student_embeddings(self):
        """Retrieve all student embeddings for training"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.student_id, s.name, ve.embedding_data
            FROM students s
            JOIN voice_embeddings ve ON s.student_id = ve.student_id
            WHERE s.is_active = 1
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        student_data = {}
        for row in results:
            student_id, name, embedding_blob = row
            embedding = pickle.loads(embedding_blob)
            
            if student_id not in student_data:
                student_data[student_id] = {
                    'name': name,
                    'embeddings': []
                }
            student_data[student_id]['embeddings'].append(embedding)
        
        return student_data
    
    def verify_student_voice(self, student_id, test_embedding, similarity_threshold=0.8):
        """Verify if test embedding matches student's registered voice"""
        try:
            print(f"🔍 [DATABASE] Verifying voice for student: {student_id}")
            print(f"📊 [DEBUG] Test embedding shape: {test_embedding.shape}")
            print(f"🎚️ [DEBUG] Similarity threshold: {similarity_threshold}")
            
            embeddings = self.get_student_embeddings(student_id)
            
            if not embeddings:
                print(f"❌ [WARNING] No embeddings found for student: {student_id}")
                return False, 0.0
            
            print(f"📊 [DEBUG] Found {len(embeddings)} stored embeddings for {student_id}")
            
            # Calculate similarity with stored embeddings
            similarities = []
            for i, emb_data in enumerate(embeddings):
                stored_embedding = emb_data['embedding']
                print(f"📊 [DEBUG] Stored embedding {i+1} shape: {stored_embedding.shape}")
                
                similarity = self.calculate_cosine_similarity(test_embedding, stored_embedding)
                similarities.append(similarity)
                print(f"📊 [DEBUG] Similarity {i+1}: {similarity:.4f}")
            
            # Use the maximum similarity
            max_similarity = max(similarities) if similarities else 0.0
            is_match = max_similarity >= similarity_threshold
            
            print(f"🎯 [RESULT] Max similarity: {max_similarity:.4f}")
            print(f"✅ [RESULT] Is match: {is_match}")
            
            return is_match, max_similarity
            
        except Exception as e:
            print(f"❌ [ERROR] Error verifying student voice: {e}")
            import traceback
            print(f"📋 [DEBUG] Traceback: {traceback.format_exc()}")
            return False, 0.0
    
    def calculate_cosine_similarity(self, embedding1, embedding2):
        """Calculate cosine similarity between two embeddings"""
        try:
            print(f"🧮 [SIMILARITY] Calculating cosine similarity...")
            print(f"📊 [DEBUG] Embedding1 shape: {embedding1.shape}")
            print(f"📊 [DEBUG] Embedding2 shape: {embedding2.shape}")
            
            # Flatten embeddings if they're multi-dimensional
            if len(embedding1.shape) > 1:
                embedding1 = embedding1.flatten()
                print(f"📊 [DEBUG] Flattened embedding1 to shape: {embedding1.shape}")
            
            if len(embedding2.shape) > 1:
                embedding2 = embedding2.flatten()
                print(f"📊 [DEBUG] Flattened embedding2 to shape: {embedding2.shape}")
            
            # Check if shapes match
            if embedding1.shape != embedding2.shape:
                print(f"❌ [ERROR] Embedding shapes don't match: {embedding1.shape} vs {embedding2.shape}")
                return 0.0
            
            # Normalize embeddings
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            print(f"📊 [DEBUG] Norm1: {norm1:.4f}, Norm2: {norm2:.4f}")
            
            if norm1 == 0 or norm2 == 0:
                print(f"⚠️ [WARNING] One of the embeddings has zero norm")
                return 0.0
            
            # Calculate dot product
            dot_product = np.dot(embedding1, embedding2)
            print(f"📊 [DEBUG] Dot product: {dot_product:.4f}")
            
            similarity = dot_product / (norm1 * norm2)
            print(f"✅ [RESULT] Cosine similarity: {similarity:.4f}")
            
            return similarity
            
        except Exception as e:
            print(f"❌ [ERROR] Error calculating cosine similarity: {e}")
            import traceback
            print(f"📋 [DEBUG] Traceback: {traceback.format_exc()}")
            return 0.0
    
    def log_login_attempt(self, student_id, success, confidence_score, ip_address=None):
        """Log login attempt for security tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO login_attempts (student_id, success, confidence_score, ip_address)
            VALUES (?, ?, ?, ?)
        ''', (student_id, success, confidence_score, ip_address))
        
        conn.commit()
        conn.close()
    
    def get_student_info(self, student_id):
        """Get student information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT student_id, name, email, registration_date, is_active
            FROM students
            WHERE student_id = ?
        ''', (student_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'student_id': result[0],
                'name': result[1],
                'email': result[2],
                'registration_date': result[3],
                'is_active': bool(result[4])
            }
        return None
    
    def list_all_students(self):
        """List all registered students"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT student_id, name, email, registration_date, is_active
            FROM students
            ORDER BY registration_date DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        students = []
        for row in results:
            students.append({
                'student_id': row[0],
                'name': row[1],
                'email': row[2],
                'registration_date': row[3],
                'is_active': bool(row[4])
            })
        
        return students
    
    def delete_student(self, student_id):
        """Delete a student and their voice data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Delete voice embeddings first
            cursor.execute('DELETE FROM voice_embeddings WHERE student_id = ?', (student_id,))
            
            # Delete login attempts
            cursor.execute('DELETE FROM login_attempts WHERE student_id = ?', (student_id,))
            
            # Delete student
            cursor.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
            
            conn.commit()
            print(f"Student {student_id} and all associated data deleted")
            return True
            
        except Exception as e:
            print(f"Error deleting student: {e}")
            return False
        finally:
            conn.close()