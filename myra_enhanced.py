#!/usr/bin/env python3
"""
🤖 Myra Voice Assistant - ENHANCED VERSION
Features:
- Fuzzy keyword matching with clarification
- Better session management (no shutting down after commands)
- Improved wake word detection
"""
import json
import os
import subprocess
import time
import webbrowser
import psutil
import pyautogui
import glob
from pathlib import Path
import re
import shutil
from datetime import datetime
import threading
import fnmatch
import random
import socket
from difflib import SequenceMatcher

# Speech recognition - prioritize speed
import speech_recognition as sr
import pyttsx3
import requests

# === Enhanced Setup ===
# TTS Engine - optimized for speed
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
        engine.setProperty('voice', voice.id)
        print(f"🎤 Using voice: {voice.name}")
        break
else:
    if len(voices) > 1:
        engine.setProperty('voice', voices[1].id)

engine.setProperty('rate', 190)
engine.setProperty('volume', 0.9)

# Fast speech recognition setup
recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.dynamic_energy_adjustment_damping = 0.15
recognizer.dynamic_energy_ratio = 1.5
recognizer.pause_threshold = 0.8
recognizer.phrase_threshold = 0.3
recognizer.non_speaking_duration = 0.8

# Enhanced wake words and keywords
WAKE_WORDS = ["myra", "hey myra", "hello myra", "hi myra"]
MEMORY_FILE = "myra_memory.json"

# Known keywords/commands for fuzzy matching
KNOWN_KEYWORDS = {
    # System commands
    "calculator": ["calc", "calculation", "calculate", "calcu"],
    "notepad": ["note pad", "text editor", "notes"],
    "chrome": ["browser", "internet", "web"],
    "volume": ["sound", "audio", "loud", "quiet"],
    "brightness": ["screen", "display", "bright", "dark"],
    "shutdown": ["turn off", "power off", "shut down"],
    "restart": ["reboot", "reset"],
    "time": ["clock", "current time", "what time"],
    "date": ["today", "current date", "what day"],
    
    # File operations
    "open": ["launch", "start", "run", "execute"],
    "search": ["find", "locate", "look for"],
    "screenshot": ["capture", "screen shot", "snap"],
    
    # AI queries
    "what": ["tell me", "explain", "describe"],
    "how": ["show me", "teach me", "guide me"],
    "weather": ["forecast", "temperature", "climate"],
    "news": ["headlines", "current events", "updates"],
    
    # Memory commands
    "remember": ["save", "store", "keep in mind"],
    "forget": ["delete", "remove", "erase"],
}

# Global state
listening_active = False
is_awake = False
session_timeout = 30  # seconds of inactivity before going back to sleep

def speak(text):
    """Fast text-to-speech"""
    print(f"🤖 Myra: {text}")
    engine.say(text)
    engine.runAndWait()

def check_internet():
    """Quick internet check"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

def fuzzy_match_keyword(user_input, threshold=0.6):
    """Find similar keywords using fuzzy matching"""
    user_input_lower = user_input.lower().strip()
    matches = []
    
    for keyword, variations in KNOWN_KEYWORDS.items():
        # Check direct keyword match
        if keyword in user_input_lower:
            matches.append((keyword, 1.0))
            continue
            
        # Check variations
        for variation in variations:
            if variation in user_input_lower:
                matches.append((keyword, 0.9))
                continue
                
        # Fuzzy matching
        keyword_similarity = SequenceMatcher(None, user_input_lower, keyword).ratio()
        if keyword_similarity >= threshold:
            matches.append((keyword, keyword_similarity))
            
        # Check against variations with fuzzy matching
        for variation in variations:
            variation_similarity = SequenceMatcher(None, user_input_lower, variation).ratio()
            if variation_similarity >= threshold:
                matches.append((keyword, variation_similarity))
    
    # Sort by similarity score and remove duplicates
    matches = list(set(matches))
    matches.sort(key=lambda x: x[1], reverse=True)
    
    return matches[:3]  # Return top 3 matches

def ask_for_clarification(matches, original_command):
    """Ask user for clarification when similar keywords are found"""
    if not matches:
        return None
        
    top_match = matches[0]
    keyword, similarity = top_match
    
    if similarity < 0.8:  # Only ask for clarification if not very confident
        clarification_responses = [
            f"Did you mean '{keyword}'? I heard '{original_command}' but I'm not sure.",
            f"I think you might be referring to '{keyword}'. Is that correct?",
            f"I heard '{original_command}'. Are you asking about '{keyword}'?",
            f"Just to clarify, when you said '{original_command}', did you mean '{keyword}'?",
        ]
        
        speak(random.choice(clarification_responses))
        
        # Listen for confirmation
        confirmation = listen_for_command()
        if confirmation and any(word in confirmation.lower() for word in ["yes", "yeah", "yep", "correct", "right", "that's right"]):
            return keyword
        elif confirmation and any(word in confirmation.lower() for word in ["no", "nope", "wrong", "not right", "different"]):
            speak("Okay, could you please rephrase what you're looking for?")
            return None
    
    return keyword

def listen_for_wake_word():
    """Listen specifically for wake words - optimized for speed"""
    global is_awake
    
    with sr.Microphone() as source:
        print("🔊 Listening for wake word...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            
            if check_internet():
                text = recognizer.recognize_google(audio, language='en-US')
            else:
                return False
                
            print(f"🗣️ Heard: {text}")
            
            # Check for wake words (including fuzzy matching)
            text_lower = text.lower().strip()
            for wake_word in WAKE_WORDS:
                if wake_word in text_lower:
                    print(f"✅ Wake word detected: {wake_word}")
                    is_awake = True
                    speak("Yes? How can I help you?")
                    return True
            
            # Fuzzy match wake words
            wake_similarity = SequenceMatcher(None, text_lower, "myra").ratio()
            if wake_similarity >= 0.7:
                print(f"✅ Fuzzy wake word detected: {text} (similarity: {wake_similarity:.2f})")
                is_awake = True
                speak("I think you called me. How can I help?")
                return True
            
            return False
            
        except sr.UnknownValueError:
            return False
        except sr.RequestError:
            print("⚠️ Speech service error")
            return False
        except sr.WaitTimeoutError:
            return False

def listen_for_command():
    """Listen for commands after wake word"""
    with sr.Microphone() as source:
        print("🎧 Listening for command...")
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)
            
            if check_internet():
                text = recognizer.recognize_google(audio, language='en-US')
            else:
                speak("Sorry, I need internet connection for speech recognition right now.")
                return ""
                
            print(f"📝 Command: {text}")
            return text.lower().strip()
            
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that. Could you repeat?")
            return ""
        except sr.RequestError:
            speak("Sorry, speech service is unavailable.")
            return ""
        except sr.WaitTimeoutError:
            print("⏰ No command heard")
            return ""

# === Memory Functions ===
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=2)

def update_memory(key, value):
    memory = load_memory()
    memory[key] = value
    save_memory(memory)

# === System Commands (same as before) ===
def handle_system_command(command):
    """Handle system commands quickly"""
    
    # Quick app launches
    if "calculator" in command or "calc" in command:
        os.system("calc")
        return "Opening calculator"
    
    elif "notepad" in command:
        os.system("notepad")
        return "Opening notepad"
    
    elif "chrome" in command:
        os.system("start chrome")
        return "Opening Chrome"
    
    # Volume controls
    elif "volume up" in command or "louder" in command:
        for _ in range(3):
            subprocess.run(["powershell", "-Command", 
                          "(New-Object -comObject WScript.Shell).SendKeys([char]175)"], 
                          check=True, capture_output=True)
        return "Volume increased"
    
    elif "volume down" in command or "quieter" in command:
        for _ in range(3):
            subprocess.run(["powershell", "-Command", 
                          "(New-Object -comObject WScript.Shell).SendKeys([char]174)"], 
                          check=True, capture_output=True)
        return "Volume decreased"
    
    elif "mute" in command:
        subprocess.run(["powershell", "-Command", 
                      "(New-Object -comObject WScript.Shell).SendKeys([char]173)"], 
                      check=True, capture_output=True)
        return "Audio muted"
    
    # Time
    elif "time" in command:
        now = datetime.now()
        return f"It's {now.strftime('%I:%M %p')}"
    
    elif "date" in command:
        now = datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}"
    
    # System info
    elif "system" in command and "info" in command:
        try:
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            return f"CPU usage: {cpu}%, Memory usage: {memory.percent}%"
        except:
            return "Couldn't get system info"
    
    return None

# === Smart File Search ===
def smart_file_search(query):
    """Fast file search"""
    try:
        matches = []
        search_paths = [
            os.path.expanduser("~\\Desktop"),
            os.path.expanduser("~\\Documents"),
            os.path.expanduser("~\\Downloads"),
            "."
        ]
        
        for search_path in search_paths:
            if not os.path.exists(search_path):
                continue
                
            for root, dirs, files in os.walk(search_path):
                if root.count(os.sep) - search_path.count(os.sep) > 2:
                    continue
                
                # Search files
                for file in files:
                    if query.lower() in file.lower():
                        matches.append(os.path.join(root, file))
                        
                # Search directories
                for dir_name in dirs:
                    if query.lower() in dir_name.lower():
                        matches.append(os.path.join(root, dir_name))
                
                if len(matches) >= 5:
                    break
            
            if matches:
                break
        
        if matches:
            first_match = matches[0]
            try:
                os.startfile(first_match)
                filename = os.path.basename(first_match)
                if len(matches) == 1:
                    return f"Opened {filename}"
                else:
                    return f"Found {len(matches)} matches. Opened {filename}"
            except:
                return f"Found {filename} but couldn't open it"
        else:
            return f"Couldn't find anything matching {query}"
            
    except Exception as e:
        return f"Search error: {str(e)}"

# === AI Response (Ollama) ===
def get_ai_response(question):
    """Quick AI response from Ollama"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": f"Answer briefly and conversationally: {question}",
                "stream": False,
                "options": {"temperature": 0.7, "top_p": 0.9}
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json().get("response", "Sorry, no response from AI")
        else:
            return "AI is not responding right now"
            
    except requests.exceptions.RequestException:
        return "AI service unavailable"

# === Enhanced Command Processing ===
def process_command(command):
    """Process user commands with fuzzy matching and clarification"""
    global is_awake
    
    # Exit commands
    if any(word in command for word in ["goodbye", "bye", "stop", "exit", "quit", "sleep"]):
        is_awake = False
        return "Goodbye! Say my name to wake me up again."
    
    # Memory commands
    elif "my name is" in command:
        name = command.split("my name is")[-1].strip()
        update_memory("user_name", name)
        return f"Nice to meet you, {name}! I'll remember that."
    
    elif "remember" in command and "my name" not in command:
        fact = command.replace("remember", "").strip()
        update_memory(f"fact_{int(time.time())}", fact)
        return f"I'll remember that {fact}"
    
    elif "what do you know about me" in command:
        memory = load_memory()
        if "user_name" in memory:
            return f"I know your name is {memory['user_name']}"
        else:
            return "I don't know much about you yet. Tell me your name!"
    
    # Try fuzzy matching for unrecognized commands
    matches = fuzzy_match_keyword(command)
    if matches:
        # Ask for clarification if needed
        clarified_keyword = ask_for_clarification(matches, command)
        if clarified_keyword:
            # Reconstruct command with clarified keyword
            command = command.replace(command.split()[0], clarified_keyword, 1)
    
    # File operations
    if "open" in command:
        search_term = command.replace("open", "").strip()
        if search_term:
            return smart_file_search(search_term)
        else:
            return "What would you like me to open?"
    
    elif "search" in command or "find" in command:
        search_term = command.replace("search", "").replace("find", "").strip()
        if search_term:
            return smart_file_search(search_term)
        else:
            return "What are you looking for?"
    
    # System commands
    system_response = handle_system_command(command)
    if system_response:
        return system_response
    
    # AI questions
    elif any(word in command for word in ["what", "how", "why", "when", "who", "where", "explain"]):
        return get_ai_response(command)
    
    # Default response with suggestion
    else:
        if matches:
            suggestions = [match[0] for match in matches[:2]]
            return f"I'm not sure what you meant. Did you mean something like: {', '.join(suggestions)}?"
        else:
            return "I can help with opening files, system commands, or answering questions. What would you like to do?"

# === Enhanced Main Loop ===
def main():
    """Enhanced main loop with better session management"""
    global is_awake
    
    print("🚀 Myra Voice Assistant - ENHANCED MODE")
    print("=" * 50)
    print("✅ Internet:", "🌐 Connected" if check_internet() else "❌ Offline")
    print("🎤 Speech Recognition: Google (Online)")
    print("🤖 AI Model: Ollama llama3.2:1b")
    print("🧠 Fuzzy Matching: Enabled")
    print("💬 Clarification: Enabled")
    print("=" * 50)
    print("💤 Myra is sleeping...")
    print("🗣️  Say 'Myra' or 'Hey Myra' to wake me up!")
    print("🛑 Press Ctrl+C to exit")
    
    last_activity_time = time.time()
    
    try:
        while True:
            current_time = time.time()
            
            if not is_awake:
                # Listen for wake word
                if listen_for_wake_word():
                    is_awake = True
                    last_activity_time = current_time
                    
                    # Main conversation loop - stay awake until timeout or explicit sleep command
                    while is_awake:
                        command = listen_for_command()
                        
                        if command:
                            last_activity_time = current_time
                            response = process_command(command)
                            speak(response)
                            
                            # Continue listening without asking "Anything else?"
                            print("🎧 Still listening... (say 'sleep' or 'goodbye' to end session)")
                        else:
                            # Check for timeout
                            if current_time - last_activity_time > session_timeout:
                                speak("I haven't heard from you for a while. Going back to sleep.")
                                is_awake = False
                                print("💤 Going back to sleep...")
                                break
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n👋 Myra shutting down. Goodbye!")
        speak("Goodbye!")

if __name__ == "__main__":
    main()
