#!/usr/bin/env python3
"""
Simple Myra test to demonstrate the enhanced features
"""
import speech_recognition as sr
import pyttsx3
import os
import fnmatch
import random

# Setup TTS
engine = pyttsx3.init()
voices = engine.getProperty('voices')
if len(voices) > 1:
    engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 180)
engine.setProperty('volume', 0.9)

def speak(text):
    print("Myra:", text)
    engine.say(text)
    engine.runAndWait()

def give_feedback():
    feedback_options = [
        "Could you wait a while as I try to fulfill your request?",
        "Please give me a sec, I'm coming.",
        "Hang tight, just processing your request now.",
        "I'm working on it, one moment please.",
    ]
    speak(random.choice(feedback_options))

def search_files(query):
    """Search for folders or files"""
    try:
        matches = []
        # Search in current directory
        for root, dirnames, filenames in os.walk('.'):  
            # Limit search depth
            if root.count(os.sep) - '.'.count(os.sep) > 3:
                continue
                
            for filename in fnmatch.filter(filenames, f'*{query}*'):
                matches.append(os.path.join(root, filename))
            for dirname in fnmatch.filter(dirnames, f'*{query}*'):
                matches.append(os.path.join(root, dirname))
            
            # Limit results
            if len(matches) >= 5:
                break
        
        if matches:
            if len(matches) == 1:
                speak(f"I found {query}. Opening it now.")
                open_file_or_folder(matches[0])
            else:
                speak(f"I found {len(matches)} items related to {query}. Opening the first one.")
                for i, match in enumerate(matches):
                    print(f"Found {i+1}: {match}")
                open_file_or_folder(matches[0])
            return matches
        else:
            speak(f"I couldn't find anything related to {query}. Could you tell me more about what {query} is?")
            return None
    except Exception as e:
        speak("Sorry, there was an error searching for the folder or file.")
        print(f"Error: {e}")
        return None

def open_file_or_folder(path):
    """Open a file or folder"""
    try:
        if os.path.isdir(path):
            os.startfile(path)
            speak(f"Opened folder: {os.path.basename(path)}")
        else:
            os.startfile(path)
            speak(f"Opened file: {os.path.basename(path)}")
    except Exception as e:
        speak("Sorry, I couldn't open that file or folder.")
        print(f"Error opening {path}: {e}")

def listen_once():
    """Listen for one command"""
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("🔊 Say something...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that.")
            return ""
        except sr.RequestError:
            speak("Sorry, speech service is down.")
            return ""
        except sr.WaitTimeoutError:
            print("Timeout - no speech detected")
            return ""

def main():
    """Simple test"""
    speak("Hi! I'm Myra. What would you like me to open?")
    
    command = listen_once()
    if not command:
        return
    
    if "open" in command.lower():
        # Extract the thing they want to open
        search_term = command.lower().replace("open", "").strip()
        if search_term:
            give_feedback()  # Give status update
            found_items = search_files(search_term)
            if found_items:
                speak("Done! Is there anything else you'd like me to help with?")
            else:
                speak("Let me try asking you differently. What exactly is squid game to you? Is it a folder, a file, or something else?")
    else:
        speak("I heard you say: " + command + ". Try saying 'open squid game' to test my new features!")

if __name__ == "__main__":
    main()
