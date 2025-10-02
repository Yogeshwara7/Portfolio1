#!/usr/bin/env python3
"""
Quick start script for the Voice Recognition Web Application
"""

import os
import sys
import webbrowser
import time
import threading

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import flask
        import numpy
        import librosa
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("\nPlease install required packages:")
        print("pip install flask numpy librosa sounddevice soundfile")
        return False

def open_browser():
    """Open browser after a short delay"""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

def main():
    print("🎤 Voice Recognition System - Web Application")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Create necessary directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('temp_audio', exist_ok=True)
    
    print("\n🚀 Starting web server...")
    print("📱 The application will open in your browser automatically")
    print("🌐 Manual URL: http://localhost:5000")
    print("\n📋 Available pages:")
    print("   • Home: http://localhost:5000")
    print("   • Register: http://localhost:5000/register")
    print("   • Voice Login: http://localhost:5000/login")
    print("   • Dashboard: http://localhost:5000/dashboard")
    
    # Open browser in background
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the web application
    try:
        from web_app import app
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down web server...")
    except Exception as e:
        print(f"\n❌ Error starting web server: {e}")
        print("\nTry running directly: python web_app.py")

if __name__ == "__main__":
    main()