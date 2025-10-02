#!/usr/bin/env python3
"""
Quick script to cleanup failed student registrations
"""

from database import VoiceDatabase

def cleanup_student(student_id):
    """Remove a student and all their data"""
    db = VoiceDatabase()
    
    # Check if student exists
    student_info = db.get_student_info(student_id)
    if not student_info:
        print(f"❌ Student {student_id} not found")
        return False
    
    print(f"👤 Found student: {student_info['name']}")
    
    # Check voice embeddings
    embeddings = db.get_student_embeddings(student_id)
    print(f"🎵 Voice embeddings: {len(embeddings)}")
    
    # Confirm deletion
    confirm = input(f"Delete student {student_id} ({student_info['name']})? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Deletion cancelled")
        return False
    
    # Delete student
    if db.delete_student(student_id):
        print(f"✅ Student {student_id} deleted successfully")
        return True
    else:
        print(f"❌ Failed to delete student {student_id}")
        return False

def list_all_students():
    """List all students"""
    db = VoiceDatabase()
    students = db.list_all_students()
    
    if not students:
        print("📭 No students found")
        return
    
    print(f"👥 Found {len(students)} students:")
    for student in students:
        embeddings = db.get_student_embeddings(student['student_id'])
        status = "✅ Complete" if len(embeddings) > 0 else "❌ No voice data"
        print(f"   {student['student_id']}: {student['name']} - {status}")

def main():
    print("🧹 Student Cleanup Tool")
    print("=" * 30)
    
    while True:
        print("\nOptions:")
        print("1. List all students")
        print("2. Delete specific student")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            list_all_students()
        elif choice == '2':
            student_id = input("Enter Student ID to delete: ").strip()
            if student_id:
                cleanup_student(student_id)
        elif choice == '3':
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()