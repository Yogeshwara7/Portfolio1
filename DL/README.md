# Student Voice Recognition Login System

A comprehensive Python-based voice recognition system that uses Convolutional Neural Networks (CNNs) to authenticate students through their voice patterns. The system allows students to register their voice by speaking a specific phrase and later use their voice for secure login authentication.

## Features

- **Voice Registration**: Students can register by speaking the phrase "Login My Account"
- **Voice Authentication**: Secure login using voice pattern recognition
- **CNN-based Recognition**: Uses deep learning for accurate speaker identification
- **Audio Preprocessing**: Advanced audio processing with MFCC and spectrogram extraction
- **Secure Database**: SQLite database for storing student information and voice embeddings
- **Dual Interface**: Both GUI (Tkinter) and CLI applications available
- **Real-time Recording**: Live audio capture and processing
- **Confidence Scoring**: Authentication with confidence thresholds
- **Student Management**: Complete CRUD operations for student records

## Technical Architecture

### Core Components

1. **preprocessing.py**: Audio preprocessing and feature extraction
   - MFCC (Mel-Frequency Cepstral Coefficients) extraction
   - Mel-spectrogram generation
   - Audio normalization and padding
   - Silence removal

2. **model.py**: CNN architecture and training
   - Deep CNN with batch normalization and dropout
   - Speaker classification and verification
   - Model saving/loading capabilities
   - Feature embedding extraction

3. **database.py**: Data management and storage
   - SQLite database for student records
   - Voice embedding storage with security hashing
   - Login attempt logging
   - Cosine similarity calculations

4. **audio_recorder.py**: Real-time audio capture
   - Cross-platform audio recording
   - Voice activity detection
   - Audio device management
   - Audio playback capabilities

5. **app.py**: GUI application (Tkinter)
   - Student registration interface
   - Voice login system
   - Student management dashboard
   - Model training interface

6. **cli_app.py**: Command-line interface
   - Batch operations support
   - Scriptable automation
   - Interactive and non-interactive modes

## Installation

### Prerequisites

- Python 3.8 or higher
- Audio input device (microphone)
- Windows/Linux/macOS

### Setup

1. Clone or download the project files
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

### Dependencies

- **tensorflow**: Deep learning framework for CNN
- **librosa**: Audio processing and feature extraction
- **numpy**: Numerical computations
- **scikit-learn**: Machine learning utilities
- **sounddevice**: Real-time audio I/O
- **soundfile**: Audio file reading/writing
- **matplotlib**: Visualization (for spectrograms)
- **tkinter**: GUI framework (usually included with Python)

## Usage

### GUI Application

Launch the graphical interface:

```bash
python app.py
```

#### Registration Process
1. Go to "Register Student" tab
2. Enter student ID, name, and email
3. Click "Record Voice" and speak "Login My Account"
4. Click "Register Student" to save

#### Login Process
1. Go to "Login" tab
2. Enter your student ID
3. Click "Record Voice for Login" and speak the phrase
4. System will authenticate and display result

#### Model Training
1. Go to "Train Model" tab
2. Click "Train Model" (requires at least 2 registered students)
3. Wait for training to complete

### Command Line Interface

#### Interactive Mode
```bash
python cli_app.py
```

#### Direct Commands

Register a student:
```bash
python cli_app.py --register STUDENT001 "John Doe" "john@email.com"
```

Login attempt:
```bash
python cli_app.py --login STUDENT001
```

Train the model:
```bash
python cli_app.py --train
```

List all students:
```bash
python cli_app.py --list
```

Delete a student:
```bash
python cli_app.py --delete STUDENT001
```

Show model information:
```bash
python cli_app.py --model-info
```

List audio devices:
```bash
python cli_app.py --devices
```

## System Architecture

### Audio Processing Pipeline

1. **Audio Capture**: Real-time recording at 22.05kHz sample rate
2. **Preprocessing**: 
   - Silence removal
   - Normalization
   - Fixed-length padding (100 frames)
3. **Feature Extraction**:
   - MFCC: 13 coefficients
   - Mel-spectrogram: 128 mel bands
4. **CNN Input**: Reshaped as 2D images for convolution

### CNN Architecture

```
Input Layer: (100, 128, 1) - Time x Frequency x Channel
├── Conv2D(32) + BatchNorm + MaxPool + Dropout(0.25)
├── Conv2D(64) + BatchNorm + MaxPool + Dropout(0.25)
├── Conv2D(128) + BatchNorm + MaxPool + Dropout(0.25)
├── Conv2D(256) + BatchNorm + GlobalAvgPool + Dropout(0.5)
├── Dense(512) + BatchNorm + Dropout(0.5)
├── Dense(256) + BatchNorm + Dropout(0.3)
└── Dense(num_classes) + Softmax
```

### Database Schema

**Students Table**:
- id (Primary Key)
- student_id (Unique)
- name
- email
- registration_date
- is_active

**Voice Embeddings Table**:
- id (Primary Key)
- student_id (Foreign Key)
- embedding_data (BLOB)
- audio_hash
- confidence_score
- registration_date

**Login Attempts Table**:
- id (Primary Key)
- student_id
- attempt_time
- success (Boolean)
- confidence_score
- ip_address

## Security Features

- **Audio Hashing**: MD5 hashing for audio integrity verification
- **Confidence Thresholds**: Configurable authentication confidence levels
- **Login Logging**: Complete audit trail of authentication attempts
- **Data Encryption**: Voice embeddings stored as encrypted binary data
- **Access Control**: Student activation/deactivation capabilities

## Configuration

### Audio Settings (preprocessing.py)
```python
sample_rate = 22050      # Audio sample rate
n_mfcc = 13             # Number of MFCC coefficients
n_fft = 2048            # FFT window size
hop_length = 512        # Hop length for STFT
max_length = 100        # Maximum sequence length
```

### Model Settings (model.py)
```python
learning_rate = 0.001   # Adam optimizer learning rate
batch_size = 32         # Training batch size
epochs = 50             # Maximum training epochs
confidence_threshold = 0.7  # Authentication threshold
```

### Database Settings (database.py)
```python
similarity_threshold = 0.8  # Cosine similarity threshold
db_path = 'voice_recognition.db'  # Database file path
```

## Performance Optimization

### Training Tips
- **Minimum Data**: At least 2-3 voice samples per student
- **Quality Audio**: Use good quality microphone in quiet environment
- **Consistent Phrase**: Always use "Login My Account" for best results
- **Regular Retraining**: Retrain model when adding new students

### Authentication Accuracy
- **Confidence Threshold**: Adjust based on security requirements
- **Multiple Samples**: Register multiple voice samples per student
- **Environmental Consistency**: Record in similar acoustic conditions

## Troubleshooting

### Common Issues

**Audio Recording Problems**:
```bash
# List available audio devices
python cli_app.py --devices

# Test microphone
python -c "import sounddevice as sd; print(sd.query_devices())"
```

**Model Training Issues**:
- Ensure at least 2 students are registered
- Check audio quality and duration
- Verify sufficient disk space for model files

**Database Errors**:
- Check file permissions for database directory
- Ensure SQLite is properly installed
- Verify database file integrity

**Import Errors**:
```bash
# Install missing dependencies
pip install -r requirements.txt

# Update TensorFlow if needed
pip install --upgrade tensorflow
```

## File Structure

```
voice_recognition_system/
├── app.py                 # GUI application
├── cli_app.py            # Command-line interface
├── preprocessing.py       # Audio preprocessing
├── model.py              # CNN model architecture
├── database.py           # Database management
├── audio_recorder.py     # Audio recording utilities
├── requirements.txt      # Python dependencies
├── README.md            # This documentation
├── voice_recognition.db  # SQLite database (created on first run)
├── voice_recognition_model.h5  # Trained model (created after training)
└── best_voice_model.h5   # Best model checkpoint (created during training)
```

## Future Enhancements

- **Multi-language Support**: Support for different languages and accents
- **Noise Robustness**: Advanced noise cancellation and filtering
- **Mobile App**: React Native or Flutter mobile application
- **Cloud Integration**: AWS/Azure cloud deployment
- **Biometric Fusion**: Combine with other biometric modalities
- **Real-time Streaming**: Continuous authentication during sessions
- **Advanced Security**: Liveness detection and anti-spoofing measures

## License

This project is provided as-is for educational and research purposes. Please ensure compliance with privacy regulations when handling biometric data.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the code documentation
3. Test with the CLI interface for debugging
4. Ensure all dependencies are properly installed