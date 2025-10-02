import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import pickle
import os

class VoiceRecognitionCNN:
    def __init__(self, input_shape, num_classes):
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.model = None
        self.history = None
        
    def build_model(self):
        """Build CNN architecture for voice recognition"""
        model = keras.Sequential([
            # First Convolutional Block
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=self.input_shape),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Second Convolutional Block
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Third Convolutional Block
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Fourth Convolutional Block
            layers.Conv2D(256, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.GlobalAveragePooling2D(),
            layers.Dropout(0.5),
            
            # Dense layers
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            # Output layer
            layers.Dense(self.num_classes, activation='softmax')
        ])
        
        self.model = model
        return model
    
    def compile_model(self, learning_rate=0.001):
        """Compile the model with optimizer and loss function"""
        optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
        
        self.model.compile(
            optimizer=optimizer,
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
    
    def train_model(self, X_train, y_train, X_val=None, y_val=None, 
                   epochs=50, batch_size=32, validation_split=0.2):
        """Train the CNN model"""
        
        # Callbacks for better training
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss', 
                patience=10, 
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss', 
                factor=0.5, 
                patience=5, 
                min_lr=1e-7
            ),
            keras.callbacks.ModelCheckpoint(
                'best_voice_model.h5',
                monitor='val_accuracy',
                save_best_only=True,
                mode='max'
            )
        ]
        
        # If validation data not provided, use validation_split
        if X_val is None or y_val is None:
            validation_data = None
        else:
            validation_data = (X_val, y_val)
            validation_split = 0.0
        
        self.history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            validation_data=validation_data,
            callbacks=callbacks,
            verbose=1
        )
        
        return self.history
    
    def evaluate_model(self, X_test, y_test):
        """Evaluate model performance"""
        test_loss, test_accuracy = self.model.evaluate(X_test, y_test, verbose=0)
        
        # Get predictions
        y_pred = self.model.predict(X_test)
        y_pred_classes = np.argmax(y_pred, axis=1)
        
        # Print classification report
        print(f"Test Accuracy: {test_accuracy:.4f}")
        print(f"Test Loss: {test_loss:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred_classes))
        
        return test_accuracy, test_loss
    
    def predict_speaker(self, audio_features, confidence_threshold=0.7):
        """Predict speaker identity with confidence score"""
        if len(audio_features.shape) == 3:
            audio_features = np.expand_dims(audio_features, axis=0)
        
        predictions = self.model.predict(audio_features, verbose=0)
        confidence = np.max(predictions)
        predicted_class = np.argmax(predictions)
        
        if confidence >= confidence_threshold:
            return predicted_class, confidence, True
        else:
            return predicted_class, confidence, False
    
    def save_model(self, model_path='voice_recognition_model.h5'):
        """Save trained model"""
        self.model.save(model_path)
        print(f"Model saved to {model_path}")
    
    def load_model(self, model_path='voice_recognition_model.h5'):
        """Load pre-trained model"""
        if os.path.exists(model_path):
            self.model = keras.models.load_model(model_path)
            print(f"Model loaded from {model_path}")
            return True
        else:
            print(f"Model file {model_path} not found")
            return False
    
    def get_feature_embeddings(self, audio_features):
        """Extract feature embeddings from the model"""
        # Create a new model that outputs from the second-to-last layer
        embedding_model = keras.Model(
            inputs=self.model.input,
            outputs=self.model.layers[-2].output
        )
        
        if len(audio_features.shape) == 3:
            audio_features = np.expand_dims(audio_features, axis=0)
        
        embeddings = embedding_model.predict(audio_features, verbose=0)
        return embeddings[0]  # Return single embedding vector