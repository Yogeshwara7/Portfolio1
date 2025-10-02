#!/usr/bin/env python3
"""
Complete Demo Script for Voice Recognition System
Demonstrates the full workflow: data generation, training, and testing
"""

import os
import sys
import time
from demo_data_generator import DemoDataGenerator
from cli_app import VoiceRecognitionCLI

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_step(step_num, title):
    """Print a formatted step"""
    print(f"\n📋 Step {step_num}: {title}")
    print("-" * 40)

def wait_for_user(message="Press Enter to continue..."):
    """Wait for user input"""
    input(f"\n⏸️  {message}")

def main():
    print_header("🎤 Voice Recognition System - Complete Demo")
    print("This demo will:")
    print("1. Generate synthetic voice data for 5 demo students")
    print("2. Train a CNN model on the generated data")
    print("3. Test the authentication system")
    print("4. Show system management features")
    
    wait_for_user("Ready to start the demo?")
    
    # Initialize components
    generator = DemoDataGenerator()
    cli = VoiceRecognitionCLI()
    
    # Step 1: Generate Demo Data
    print_step(1, "Generating Demo Students with Synthetic Voice Data")
    
    # Clean up any existing demo data first
    generator.cleanup_demo_data()
    
    # Create 5 demo students
    generator.create_demo_students(5)
    
    wait_for_user("Demo students created! Check the student list?")
    
    # Show created students
    print("\n📊 Current Students in Database:")
    cli.list_students()
    
    wait_for_user("Ready to train the model?")
    
    # Step 2: Train the Model
    print_step(2, "Training CNN Model on Voice Data")
    
    success = cli.train_model()
    
    if not success:
        print("❌ Training failed! Cannot continue with demo.")
        return
    
    wait_for_user("Model trained! Ready to test authentication?")
    
    # Step 3: Test Authentication
    print_step(3, "Testing Voice Authentication")
    
    print("🧪 Testing authentication with demo students...")
    
    # Test with existing students
    test_students = ["DEMO001", "DEMO002", "DEMO003"]
    
    for student_id in test_students:
        print(f"\n🎯 Testing authentication for {student_id}")
        
        # Get student info
        student_info = cli.db.get_student_info(student_id)
        if student_info:
            print(f"Student: {student_info['name']}")
            
            # Generate a test voice sample
            print("Generating synthetic test voice...")
            
            # Get one of the stored embeddings to simulate authentication
            embeddings = cli.db.get_student_embeddings(student_id)
            if embeddings:
                test_embedding = embeddings[0]['embedding']
                
                # Test verification
                is_match, similarity = cli.db.verify_student_voice(student_id, test_embedding)
                
                if is_match:
                    print(f"✅ Authentication SUCCESS for {student_info['name']}")
                    print(f"   Similarity: {similarity:.2%}")
                else:
                    print(f"❌ Authentication FAILED for {student_info['name']}")
                    print(f"   Similarity: {similarity:.2%}")
                
                # Log the attempt
                cli.db.log_login_attempt(student_id, is_match, similarity)
            else:
                print(f"❌ No voice data found for {student_id}")
        
        time.sleep(1)  # Small delay for readability
    
    wait_for_user("Authentication tests completed! Ready to see model info?")
    
    # Step 4: Show Model Information
    print_step(4, "Model and System Information")
    
    cli.show_model_info()
    
    wait_for_user("Ready to see system management features?")
    
    # Step 5: System Management Demo
    print_step(5, "System Management Features")
    
    print("\n📈 Database Statistics:")
    students = cli.db.list_all_students()
    print(f"Total Students: {len(students)}")
    
    # Count voice embeddings
    total_embeddings = 0
    for student in students:
        embeddings = cli.db.get_student_embeddings(student['student_id'])
        total_embeddings += len(embeddings)
    
    print(f"Total Voice Samples: {total_embeddings}")
    
    # Show login attempts
    print(f"\n📊 Recent Login Attempts:")
    print("(Simulated from our authentication tests)")
    
    wait_for_user("Ready to test with custom audio files?")
    
    # Step 6: Generate Test Audio Files
    print_step(6, "Generating Test Audio Files")
    
    generator.generate_test_audio_files()
    
    print("\n🎵 Test audio files created in 'demo_audio' directory")
    print("You can use these files to test the system manually:")
    print("- Load them in the GUI application")
    print("- Analyze their characteristics")
    print("- Test preprocessing pipeline")
    
    wait_for_user("Ready to see cleanup options?")
    
    # Step 7: Cleanup Options
    print_step(7, "Demo Cleanup")
    
    print("Demo completed successfully! 🎉")
    print("\nWhat's next?")
    print("1. Use the GUI application: python app.py")
    print("2. Use CLI for more operations: python cli_app.py --help")
    print("3. Train with real voice data")
    print("4. Integrate into your own applications")
    
    print("\nCleanup options:")
    print("- Keep demo data for further testing")
    print("- Remove demo data to start fresh")
    
    cleanup = input("\nRemove demo data? (y/n): ").lower().strip()
    
    if cleanup == 'y':
        generator.cleanup_demo_data()
        
        # Also remove model files if user wants
        model_cleanup = input("Remove trained model files? (y/n): ").lower().strip()
        if model_cleanup == 'y':
            model_files = ['voice_recognition_model.h5', 'best_voice_model.h5']
            for model_file in model_files:
                if os.path.exists(model_file):
                    os.remove(model_file)
                    print(f"✅ Removed {model_file}")
        
        print("🧹 Cleanup completed!")
    else:
        print("📦 Demo data preserved for further testing")
    
    print_header("🎉 Demo Completed Successfully!")
    print("Thank you for trying the Voice Recognition System!")
    print("\nFor more information, check:")
    print("- README.md for detailed documentation")
    print("- requirements.txt for dependencies")
    print("- Individual module files for implementation details")

def quick_demo():
    """Run a quick automated demo without user interaction"""
    print_header("🚀 Quick Automated Demo")
    
    generator = DemoDataGenerator()
    cli = VoiceRecognitionCLI()
    
    print("🔄 Running automated demo...")
    
    # Cleanup and create demo data
    generator.cleanup_demo_data()
    generator.create_demo_students(3)  # Fewer students for quick demo
    
    # Train model
    print("\n🤖 Training model...")
    cli.train_model()
    
    # Test authentication
    print("\n🧪 Testing authentication...")
    test_students = ["DEMO001", "DEMO002"]
    
    for student_id in test_students:
        student_info = cli.db.get_student_info(student_id)
        embeddings = cli.db.get_student_embeddings(student_id)
        
        if embeddings:
            test_embedding = embeddings[0]['embedding']
            is_match, similarity = cli.db.verify_student_voice(student_id, test_embedding)
            
            status = "✅ SUCCESS" if is_match else "❌ FAILED"
            print(f"{status} - {student_info['name']}: {similarity:.2%}")
    
    print("\n🎉 Quick demo completed!")
    print("Run 'python run_demo.py' for the full interactive demo")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_demo()
    else:
        main()