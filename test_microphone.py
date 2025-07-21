#!/usr/bin/env python3
"""
Test microphone functionality
"""
import speech_recognition as sr
import time

def test_microphone():
    print("🎤 Testing microphone...")
    recognizer = sr.Recognizer()
    
    # List available microphones
    print("\n📱 Available microphones:")
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"  {index}: {name}")
    
    try:
        with sr.Microphone() as source:
            print("\n📡 Calibrating microphone...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print(f"✅ Energy threshold: {recognizer.energy_threshold}")
            
            print("\n🔊 Say something (you have 5 seconds):")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            print("🔍 Processing audio...")
            
        # Try to recognize what was said
        try:
            text = recognizer.recognize_google(audio)
            print(f"✅ You said: '{text}'")
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
        except sr.RequestError as e:
            print(f"❌ Could not request results: {e}")
            
    except sr.WaitTimeoutError:
        print("⏰ Timeout - no speech detected")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_microphone()
