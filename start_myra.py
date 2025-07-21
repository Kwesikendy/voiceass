#!/usr/bin/env python3
"""
🤖 Myra Voice Assistant Launcher
Quick setup and launch script for your AI assistant
"""

import sys
import os
import subprocess

def check_requirements():
    """Check if all required packages are installed"""
    required_packages = [
        'speech_recognition',
        'pyttsx3', 
        'requests',
        'psutil',
        'pyautogui'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_missing_packages(packages):
    """Install missing packages"""
    if packages:
        print(f"📦 Installing missing packages: {', '.join(packages)}")
        for package in packages:
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
        print("✅ All packages installed!")

def check_ollama():
    """Check if Ollama is running and has models"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            if models.get('models'):
                print(f"✅ Ollama is running with {len(models['models'])} model(s)")
                return True
            else:
                print("⚠️  Ollama is running but no models are installed")
                print("   Run: ollama pull llama3.2:1b")
                return False
        else:
            print("❌ Ollama is not responding")
            return False
    except Exception as e:
        print("❌ Cannot connect to Ollama")
        print("   Make sure Ollama is installed and running")
        return False

def main():
    print("🚀 Starting Myra Voice Assistant Setup...")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check and install requirements
    missing = check_requirements()
    if missing:
        try:
            install_missing_packages(missing)
        except Exception as e:
            print(f"❌ Failed to install packages: {e}")
            return
    else:
        print("✅ All required packages are installed")
    
    # Check Ollama
    ollama_ready = check_ollama()
    
    print("\n" + "=" * 50)
    print("🤖 Myra Voice Assistant Ready!")
    print("=" * 50)
    print("🗣️  Wake words: 'Hello Myra', 'Hey Myra', 'Hi Myra'")
    print("💤 Myra will sleep until you call her name")
    print("🛑 Press Ctrl+C to stop")
    
    if not ollama_ready:
        print("\n⚠️  Warning: AI features may not work without Ollama models")
        
    print("\n🎬 Starting Myra in 3 seconds...")
    
    import time
    time.sleep(3)
    
    # Change to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Launch Myra
    try:
        import myra_wake_word
        myra_wake_word.main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting Myra: {e}")
        print("Check that myra_wake_word.py is in the same directory")

if __name__ == "__main__":
    main()
