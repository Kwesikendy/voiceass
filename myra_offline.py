#!/usr/bin/env python3
"""
🤖 Myra Voice Assistant - OFFLINE VERSION
Complete voice assistant that works without internet!
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

# Offline speech recognition
import vosk
import pyaudio

# Text to speech
import pyttsx3

# For AI responses (Ollama - runs locally)
import requests

# === Setup ===
# TTS Engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if 'female' in voice.name.lower() or 'zira' in voice.name.lower() or 'hazel' in voice.name.lower():
        engine.setProperty('voice', voice.id)
        print(f"🎤 Using voice: {voice.name}")
        break
else:
    if len(voices) > 1:
        engine.setProperty('voice', voices[1].id)
        print(f"🎤 Using voice: {voices[1].name}")
    else:
        print(f"🎤 Using default voice")

engine.setProperty('rate', 180)
engine.setProperty('volume', 0.9)

# Vosk model setup
MODEL_PATH = "vosk-model"
if not os.path.exists(MODEL_PATH):
    print("❌ Vosk model not found. Please run download_vosk_model.py first")
    exit(1)

# Initialize Vosk
model = vosk.Model(MODEL_PATH)
rec = vosk.KaldiRecognizer(model, 16000)
rec.SetWords(True)

# Audio setup
audio = pyaudio.PyAudio()

# Ollama setup (local AI)
OLLAMA_URL = "http://localhost:11434/api/generate"

# Wake words
WAKE_WORDS = ["hello myra", "hey myra", "hi myra", "myra", "okay myra"]

MEMORY_FILE = "myra_memory.json"

# Load memory
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save memory
def save_memory(memory):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=4)


# Update memory context
def update_memory(key, value):
    memory = load_memory()
    memory[key] = value
    save_memory(memory)

# Recall memory context
def recall_memory(key):
    memory = load_memory()
    return memory.get(key, None)

# Forget a specific memory
def forget_memory(key):
    memory = load_memory()
    if key in memory:
        del memory[key]
        save_memory(memory)
    

# Global state
listening_active = False

def get_available_models():
    """Get list of available Ollama models"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json()
            return [model['name'] for model in models.get('models', [])]
        return []
    except:
        return []

def select_model():
    """Automatically select the best available model"""
    models = get_available_models()
    if not models:
        print("⚠️  No Ollama models found. AI features will be limited.")
        return None
    
    preferred_models = [
        'llama3.2:3b', 'llama3.2:1b', 'llama3.1:8b', 'llama3.1:7b',
        'mistral:7b', 'mistral:latest', 'gemma:7b', 'codellama:7b'
    ]
    
    for preferred in preferred_models:
        if preferred in models:
            print(f"✅ Using AI model: {preferred}")
            return preferred
    
    selected = models[0]
    print(f"✅ Using AI model: {selected}")
    return selected

MODEL_NAME = select_model()

def speak(text):
    """Text to speech function"""
    print("Myra:", text)
    engine.say(text)
    engine.runAndWait()

def listen_offline():
    """Listen using Vosk offline speech recognition"""
    stream = audio.open(format=pyaudio.paInt16,
                       channels=1,
                       rate=16000,
                       input=True,
                       frames_per_buffer=8000)
    
    stream.start_stream()
    
    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get('text', '').strip()
                if text:
                    return text
            else:
                partial = json.loads(rec.PartialResult())
                # You can use partial results for real-time feedback if needed
                
    except Exception as e:
        print(f"Error in speech recognition: {e}")
        return ""
    finally:
        stream.stop_stream()
        stream.close()

def check_wake_word(command):
    """Check if wake word is detected"""
    command_lower = command.lower()
    
    # Direct matches
    if any(wake_word in command_lower for wake_word in WAKE_WORDS):
        return True
        
    # Handle common misrecognitions
    misrecognitions = {
        "mirror": "myra", "maria": "myra", "mira": "myra", "maya": "myra"
    }
    
    for misrecognition, correct in misrecognitions.items():
        if misrecognition in command_lower:
            print(f"🔧 Corrected '{misrecognition}' to '{correct}'")
            return True
            
    return False

def remember_conversation(statement):
    """Decide whether to remember something from the conversation"""
    lower_statement = statement.lower()

    # Simple rules to remember specific facts
    if "my name is" in lower_statement:
        name = lower_statement.split("my name is")[-1].strip()
        update_memory("user_name", name)
        speak(f"Nice to meet you, {name}")
    elif "remember" in lower_statement:
        remember_key = lower_statement.replace("remember", "").strip()
        update_memory(remember_key, True)
        speak(f"I'll remember {remember_key}")
    elif "forget" in lower_statement:
        forget_key = lower_statement.replace("forget", "").strip()
        forget_memory(forget_key)
        speak(f"I forgot about {forget_key}")


def give_feedback():
    """Provide user with real-time status updates"""
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
        # Search in current directory and common locations
        search_paths = ['.', os.path.expanduser('~')]
        
        for search_path in search_paths:
            if os.path.exists(search_path):
                for root, dirnames, filenames in os.walk(search_path):
                    # Limit search depth
                    if root.count(os.sep) - search_path.count(os.sep) > 3:
                        continue
                    
                    for filename in fnmatch.filter(filenames, f'*{query}*'):
                        matches.append(os.path.join(root, filename))
                    for dirname in fnmatch.filter(dirnames, f'*{query}*'):
                        matches.append(os.path.join(root, dirname))
                    
                    if len(matches) >= 10:
                        break
        
        if matches:
            if len(matches) == 1:
                speak(f"I found {query}. Opening it now.")
                open_file_or_folder(matches[0])
            else:
                speak(f"I found {len(matches)} items related to {query}. Opening the first one.")
                for i, match in enumerate(matches[:5]):
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

def adjust_brightness(action):
    """Adjust screen brightness"""
    try:
        action_lower = action.lower()
        
        increase_words = ["increase", "up", "higher", "brighter", "bright", "more", "raise", "turn up", "boost", "max", "maximum"]
        decrease_words = ["decrease", "down", "lower", "darker", "dark", "less", "dim", "reduce", "turn down", "minimize", "min", "minimum"]
        
        percentage_match = re.search(r'(\d+)\s*(?:percent|%)?', action_lower)
        
        if percentage_match:
            percentage = int(percentage_match.group(1))
            percentage = max(10, min(100, percentage))
            subprocess.run(["powershell", "-Command", 
                          f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {percentage})"], 
                          check=True, capture_output=True)
            return f"Brightness set to {percentage} percent."
        elif any(word in action_lower for word in increase_words):
            subprocess.run(["powershell", "-Command", 
                          "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, 100)"], 
                          check=True, capture_output=True)
            return "Brightness increased to maximum."
        elif any(word in action_lower for word in decrease_words):
            subprocess.run(["powershell", "-Command", 
                          "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, 30)"], 
                          check=True, capture_output=True)
            return "Brightness decreased to 30 percent."
        else:
            return "I can make your screen brighter or darker. What would you prefer?"
            
    except Exception as e:
        return "Sorry, I couldn't adjust the brightness. This might require administrator privileges."

def control_system(command):
    """Handle all system control commands"""
    command_lower = command.lower()
    
    # System power commands
    if any(x in command_lower for x in ["shutdown", "turn off", "power off"]):
        speak("Shutting down the computer in 10 seconds. Say cancel to stop.")
        time.sleep(3)
        speak("Shutting down now.")
        try:
            os.system("shutdown /s /t 5")
            return "Computer is shutting down."
        except:
            return "Sorry, I couldn't shut down the computer."
    
    elif any(x in command_lower for x in ["restart", "reboot"]):
        speak("Restarting the computer in 10 seconds. Say cancel to stop.")
        time.sleep(3)
        speak("Restarting now.")
        try:
            os.system("shutdown /r /t 5")
            return "Computer is restarting."
        except:
            return "Sorry, I couldn't restart the computer."
    
    elif any(x in command_lower for x in ["lock", "lock screen", "lock computer"]):
        try:
            os.system("rundll32.exe user32.dll, LockWorkStation")
            return "Screen locked."
        except:
            return "Sorry, I couldn't lock the screen."
    
    elif any(x in command_lower for x in ["sleep", "hibernate"]):
        try:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "Computer is going to sleep."
        except:
            return "Sorry, I couldn't put the computer to sleep."
    
    # Brightness and volume controls
    elif any(x in command_lower for x in ["brightness", "brighter", "darker", "dim"]):
        return adjust_brightness(command_lower)
    
    elif "volume" in command_lower or "sound" in command_lower:
        # Volume control logic (same as before)
        volume_up_words = ["up", "increase", "higher", "louder", "more"]
        volume_down_words = ["down", "decrease", "lower", "quieter", "less"]
        mute_words = ["mute", "silence", "quiet", "off"]
        
        try:
            if any(word in command_lower for word in mute_words):
                subprocess.run(["powershell", "-Command", 
                              "(New-Object -comObject WScript.Shell).SendKeys([char]173)"], 
                              check=True, capture_output=True)
                return "Audio muted."
            elif any(word in command_lower for word in volume_up_words):
                for _ in range(5):
                    subprocess.run(["powershell", "-Command", 
                                  "(New-Object -comObject WScript.Shell).SendKeys([char]175)"], 
                                  check=True, capture_output=True)
                    time.sleep(0.1)
                return "Volume increased."
            elif any(word in command_lower for word in volume_down_words):
                for _ in range(5):
                    subprocess.run(["powershell", "-Command", 
                                  "(New-Object -comObject WScript.Shell).SendKeys([char]174)"], 
                                  check=True, capture_output=True)
                    time.sleep(0.1)
                return "Volume decreased."
        except:
            return "Sorry, I couldn't adjust the volume."
    
    # Application management
    elif any(x in command_lower for x in ["calculator", "notepad", "chrome", "firefox", "edge"]):
        app_mapping = {
            "calculator": "calc", "notepad": "notepad", 
            "chrome": "chrome", "firefox": "firefox", "edge": "msedge"
        }
        for app_word, app_cmd in app_mapping.items():
            if app_word in command_lower:
                try:
                    if "close" in command_lower:
                        os.system(f"taskkill /f /im {app_cmd}.exe")
                        return f"{app_word.title()} closed."
                    else:
                        os.system(app_cmd)
                        return f"{app_word.title()} opened."
                except:
                    return f"Sorry, I couldn't handle {app_word.title()}."
    
    # System info
    elif "system info" in command_lower or "pc info" in command_lower:
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:\\\\')
            return f"CPU usage: {cpu_usage}%, Memory usage: {memory.percent}%, Disk usage: {disk.percent}%."
        except:
            return "Sorry, I couldn't get system information."
    
    # Time and date
    elif "time" in command_lower or "date" in command_lower:
        now = datetime.now()
        if "time" in command_lower:
            return f"The current time is {now.strftime('%I:%M %p')}."
        else:
            return f"Today is {now.strftime('%A, %B %d, %Y')}."
    
    # Screenshot
    elif "screenshot" in command_lower:
        try:
            screenshot = pyautogui.screenshot()
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot.save(filename)
            return f"Screenshot saved as {filename}."
        except:
            return "Sorry, I couldn't take a screenshot."
    
    return None

def get_memory_context():
    """Get a formatted string of what Myra knows about the user"""
    memory = load_memory()
    if not memory:
        return None
    
    context_parts = []
    for key, value in memory.items():
        if key == "user_name":
            context_parts.append(f"User's name is {value}")
        elif key == "last_conversation":
            context_parts.append(f"Last talked about: {value}")
        elif isinstance(value, str):
            context_parts.append(f"{key}: {value}")
        elif value is True:
            context_parts.append(f"User asked to remember: {key}")
    
    return "; ".join(context_parts) if context_parts else None

def handle_memory_command(command):
    """Handle memory-specific commands"""
    command_lower = command.lower()
    
    if "my name is" in command_lower:
        name = command_lower.split("my name is")[-1].strip()
        update_memory("user_name", name)
        update_memory("last_conversation", f"introduced themselves as {name}")
        speak(f"Nice to meet you, {name}! I'll remember that.")
        
    elif "remember that" in command_lower:
        fact = command_lower.replace("remember that", "").strip()
        update_memory(f"fact_{len(load_memory())}", fact)
        update_memory("last_conversation", f"asked me to remember: {fact}")
        speak(f"Got it, I'll remember that {fact}.")
        
    elif "remember" in command_lower and "that" not in command_lower:
        fact = command_lower.replace("remember", "").strip()
        update_memory(f"remember_{len(load_memory())}", fact)
        speak(f"I'll remember {fact}.")
        
    elif "forget about" in command_lower:
        forget_item = command_lower.replace("forget about", "").strip()
        memory = load_memory()
        keys_to_delete = []
        for key, value in memory.items():
            if forget_item in str(value).lower() or forget_item in key.lower():
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            forget_memory(key)
        
        if keys_to_delete:
            speak(f"I've forgotten about {forget_item}.")
        else:
            speak(f"I don't recall anything about {forget_item} to forget.")
            
    elif "do you remember" in command_lower:
        memory_item = command_lower.replace("do you remember", "").strip()
        memory = load_memory()
        found_memories = []
        
        for key, value in memory.items():
            if memory_item in str(value).lower() or memory_item in key.lower():
                found_memories.append((key, value))
        
        if found_memories:
            speak(f"Yes, I remember about {memory_item}.")
            for key, value in found_memories[:2]:  # Limit to avoid long responses
                if isinstance(value, str):
                    speak(f"I know that {value}.")
        else:
            speak(f"I don't have any memories about {memory_item}.")
            
    elif "what do you know about me" in command_lower:
        memory = load_memory()
        if not memory:
            speak("I don't know much about you yet. Tell me about yourself!")
            return
        
        speak("Here's what I remember about you:")
        count = 0
        for key, value in memory.items():
            if count >= 3:  # Limit to avoid overwhelming
                break
            if key == "user_name":
                speak(f"Your name is {value}.")
                count += 1
            elif isinstance(value, str) and not key.startswith("last_"):
                speak(f"I remember that {value}.")
                count += 1
        
        if count == 0:
            speak("I have some information stored, but it's mostly system data. Tell me more about yourself!")

def ask_ollama(prompt):
    """Get AI response from Ollama (local)"""
    if not MODEL_NAME:
        return "Sorry, no AI model is available. But I can still help with system commands!"
    
    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False  # Non-streaming for simplicity
        }
        response = requests.post(OLLAMA_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('response', 'Sorry, I got an empty response.')
        else:
            return "Sorry, the AI service isn't responding right now."
            
    except requests.exceptions.Timeout:
        return "The AI is taking too long to respond."
    except requests.exceptions.ConnectionError:
        return "I can't connect to the AI service right now, but I can still help with system commands."
    except Exception as e:
        return "Sorry, there was an error with the AI response."

def main_loop():
    """Main conversation loop"""
    global listening_active
    
    print("🤖 Myra Voice Assistant - OFFLINE MODE")
    print("💤 Myra is sleeping...")
    print("🗣️  Wake words: 'Hello Myra', 'Hey Myra', 'Hi Myra'")
    print("🛑 Press Ctrl+C to stop")
    print("🔊 Say 'Hello Myra' to wake me up...")
    
    while True:
        try:
            if not listening_active:
                # Listen for wake word
                command = listen_offline()
                if command:
                    print(f"🔍 Heard: {command}")
                    if check_wake_word(command):
                        print("🚀 Wake word detected! Activating Myra...")
                        listening_active = True
                        
                        # Personalized greeting based on memory
                        user_name = recall_memory("user_name")
                        if user_name:
                            greetings = [
                                f"Hi {user_name}! I'm awake and ready to help.",
                                f"Hello {user_name}! What can I do for you today?",
                                f"Hey {user_name}! Good to hear from you again.",
                            ]
                            speak(random.choice(greetings))
                        else:
                            speak("Hi! I'm awake and ready to help. What can I do for you?")
            else:
                # Active listening mode
                print("👂 Listening...")
                command = listen_offline()
                
                if not command:
                    continue
                
                print(f"You: {command}")
                
                # Check for sleep commands
                if any(x in command.lower() for x in ["go to sleep", "sleep now", "goodbye myra", "that's all"]):
                    speak("Going back to sleep. Say 'Hello Myra' to wake me up again.")
                    listening_active = False
                    continue
                
                # Handle system commands
                system_response = control_system(command)
                if system_response:
                    speak(system_response)
                    continue
                
                # Check for memory-related commands first
                if any(phrase in command.lower() for phrase in ["my name is", "remember", "forget", "do you remember", "what do you know about me"]):
                    handle_memory_command(command)
                    continue
                
                # Handle file operations
                if "open" in command.lower():
                    search_term = command.lower().replace("open", "").strip()
                    if search_term:
                        give_feedback()
                        found_items = search_files(search_term)
                        if found_items:
                            continue
                
                # AI conversation with memory context
                if command.strip():
                    # Add memory context to AI prompts
                    memory_context = get_memory_context()
                    if memory_context:
                        enhanced_prompt = f"Context about user: {memory_context}\n\nUser says: {command}"
                    else:
                        enhanced_prompt = command
                    
                    answer = ask_ollama(enhanced_prompt)
                    if answer:
                        speak(answer)
                        
                        # Remember important information from the conversation
                        remember_conversation(command)
                        
        except KeyboardInterrupt:
            print("\n👋 Myra is shutting down. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main_loop()
    finally:
        audio.terminate()
