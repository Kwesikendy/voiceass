#!/usr/bin/env python3
"""
🤖 Myra Voice Assistant - OPTIMIZED OFFLINE VERSION
Fast Vosk speech recognition with performance optimizations
"""
import json
import os
import subprocess
import time
import psutil
import pyautogui
from datetime import datetime
import threading
import queue
import socket

# Speech recognition - optimized offline
try:
    import vosk
    import pyaudio
    VOSK_AVAILABLE = True
except ImportError:
    print("❌ Vosk not available - install with: pip install vosk pyaudio")
    exit(1)

# Fallback online
import speech_recognition as sr
import pyttsx3
import requests

# === OPTIMIZED VOSK SETUP ===
MODEL_PATH = "vosk-model"
if not os.path.exists(MODEL_PATH):
    print("❌ Vosk model not found. Run download_vosk_model.py first")
    exit(1)

# Pre-load model for faster startup
print("🔄 Loading optimized speech model...")
model = vosk.Model(MODEL_PATH)

# Optimized recognizer settings
rec = vosk.KaldiRecognizer(model, 16000)
rec.SetWords(True)
rec.SetPartialWords(True)  # Enable partial recognition for faster feedback

# Audio stream settings - optimized for speed
CHUNK = 1024  # Smaller chunks for lower latency
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

audio = pyaudio.PyAudio()
print("✅ Offline speech recognition optimized and ready")

# === FAST TTS SETUP ===
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break
else:
    if len(voices) > 1:
        engine.setProperty('voice', voices[1].id)

engine.setProperty('rate', 200)  # Faster speech
engine.setProperty('volume', 0.9)

# === GLOBAL SETTINGS ===
WAKE_WORDS = ["myra", "hey myra", "hello myra", "hi myra"]
MEMORY_FILE = "myra_memory.json"
is_awake = False

# Audio processing queue for threading
audio_queue = queue.Queue()
result_queue = queue.Queue()

def speak(text):
    """Fast text-to-speech"""
    print(f"🤖 Myra: {text}")
    engine.say(text)
    engine.runAndWait()

def check_internet():
    """Quick internet check"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=1)
        return True
    except OSError:
        return False

class OptimizedVoskListener:
    """Optimized Vosk listener with threading for better performance"""
    
    def __init__(self):
        self.stream = None
        self.listening = False
        self.partial_result = ""
        
    def start_stream(self):
        """Start optimized audio stream"""
        self.stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=self.audio_callback
        )
        self.stream.start_stream()
        
    def audio_callback(self, in_data, frame_count, time_info, status):
        """Audio callback for continuous processing"""
        if self.listening:
            audio_queue.put(in_data)
        return (in_data, pyaudio.paContinue)
    
    def stop_stream(self):
        """Stop audio stream"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
    
    def listen_for_wake_word(self, timeout=5):
        """Optimized wake word detection"""
        print("🔊 Listening for wake word...")
        self.listening = True
        start_time = time.time()
        
        # Clear any old data
        while not audio_queue.empty():
            audio_queue.get()
        
        while time.time() - start_time < timeout:
            try:
                data = audio_queue.get(timeout=0.1)
                
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get('text', '').strip()
                    
                    if text:
                        print(f"🗣️ Heard: {text}")
                        
                        # Check for wake words
                        for wake_word in WAKE_WORDS:
                            if wake_word in text.lower():
                                print(f"✅ Wake word detected: {wake_word}")
                                self.listening = False
                                return True
                
                else:
                    # Check partial results for immediate feedback
                    partial = json.loads(rec.PartialResult())
                    partial_text = partial.get('partial', '').strip()
                    
                    if partial_text and partial_text != self.partial_result:
                        self.partial_result = partial_text
                        print(f"🎧 Partial: {partial_text}")
                        
                        # Quick wake word check on partial results
                        for wake_word in WAKE_WORDS:
                            if wake_word in partial_text.lower():
                                print(f"✅ Wake word detected (partial): {wake_word}")
                                self.listening = False
                                return True
                                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠️ Audio processing error: {e}")
                continue
        
        self.listening = False
        return False
    
    def listen_for_command(self, timeout=10):
        """Optimized command listening"""
        print("🎧 Listening for command...")
        self.listening = True
        start_time = time.time()
        command_parts = []
        
        # Clear queue
        while not audio_queue.empty():
            audio_queue.get()
        
        while time.time() - start_time < timeout:
            try:
                data = audio_queue.get(timeout=0.5)
                
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get('text', '').strip()
                    
                    if text:
                        command_parts.append(text)
                        print(f"📝 Command part: {text}")
                        
                        # If we get a complete phrase, process it
                        if len(text.split()) >= 2:
                            full_command = ' '.join(command_parts)
                            self.listening = False
                            return full_command
                
                else:
                    # Show partial results for user feedback
                    partial = json.loads(rec.PartialResult())
                    partial_text = partial.get('partial', '').strip()
                    
                    if partial_text and partial_text != self.partial_result:
                        self.partial_result = partial_text
                        print(f"🎧 Hearing: {partial_text}")
                        
            except queue.Empty:
                # Check if we have accumulated command parts
                if command_parts:
                    full_command = ' '.join(command_parts)
                    if len(full_command.split()) >= 1:  # At least one word
                        self.listening = False
                        return full_command
                continue
            except Exception as e:
                print(f"⚠️ Command processing error: {e}")
                continue
        
        self.listening = False
        # Return any accumulated command
        if command_parts:
            return ' '.join(command_parts)
        return ""

# Initialize optimized listener
vosk_listener = OptimizedVoskListener()

# === MEMORY FUNCTIONS ===
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

# === QUICK SYSTEM COMMANDS ===
def handle_system_command(command):
    """Handle system commands quickly"""
    
    if "calculator" in command or "calc" in command:
        os.system("calc")
        return "Opening calculator"
    
    elif "notepad" in command:
        os.system("notepad")
        return "Opening notepad"
    
    elif "chrome" in command:
        os.system("start chrome")
        return "Opening Chrome"
    
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
    
    elif "time" in command:
        now = datetime.now()
        return f"It's {now.strftime('%I:%M %p')}"
    
    elif "date" in command:
        now = datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}"
    
    elif "system" in command and "info" in command:
        try:
            cpu = psutil.cpu_percent(interval=0.1)  # Faster system check
            memory = psutil.virtual_memory()
            return f"CPU usage: {cpu}%, Memory usage: {memory.percent}%"
        except:
            return "Couldn't get system info"
    
    return None

# === SMART FILE SEARCH ===
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
                if root.count(os.sep) - search_path.count(os.sep) > 1:  # Limit depth
                    continue
                
                for file in files:
                    if query.lower() in file.lower():
                        matches.append(os.path.join(root, file))
                        
                for dir_name in dirs:
                    if query.lower() in dir_name.lower():
                        matches.append(os.path.join(root, dir_name))
                
                if len(matches) >= 3:  # Limit for speed
                    break
            
            if matches:
                break
        
        if matches:
            first_match = matches[0]
            try:
                os.startfile(first_match)
                filename = os.path.basename(first_match)
                return f"Opened {filename}"
            except:
                return f"Found {filename} but couldn't open it"
        else:
            return f"Couldn't find anything matching {query}"
            
    except Exception as e:
        return f"Search error: {str(e)}"

# === AI RESPONSE (OLLAMA) ===
def get_ai_response(question):
    """Quick AI response from Ollama"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": f"Answer briefly in 1-2 sentences: {question}",
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 50}  # Limit response length
            },
            timeout=8
        )
        
        if response.status_code == 200:
            return response.json().get("response", "Sorry, no response from AI")
        else:
            return "AI is not responding right now"
            
    except:
        return "AI service unavailable"

# === COMMAND PROCESSING ===
def process_command(command):
    """Process user commands quickly"""
    global is_awake
    
    if any(word in command for word in ["goodbye", "bye", "stop", "exit", "quit"]):
        is_awake = False
        return "Goodbye! Say my name to wake me up again."
    
    elif "my name is" in command:
        name = command.split("my name is")[-1].strip()
        update_memory("user_name", name)
        return f"Nice to meet you, {name}!"
    
    elif "remember" in command and "my name" not in command:
        fact = command.replace("remember", "").strip()
        update_memory(f"fact_{int(time.time())}", fact)
        return f"I'll remember that {fact}"
    
    elif "what do you know about me" in command:
        memory = load_memory()
        if "user_name" in memory:
            return f"I know your name is {memory['user_name']}"
        else:
            return "Tell me your name first!"
    
    elif "open" in command:
        search_term = command.replace("open", "").strip()
        if search_term:
            return smart_file_search(search_term)
        else:
            return "What would you like me to open?"
    
    # System commands
    system_response = handle_system_command(command)
    if system_response:
        return system_response
    
    # AI questions
    elif any(word in command for word in ["what", "how", "why", "when", "who", "where"]):
        return get_ai_response(command)
    
    else:
        return "I can help with opening files, system commands, or answering questions!"

# === MAIN LOOP ===
def main():
    """Optimized main loop"""
    global is_awake
    
    print("🚀 Myra Voice Assistant - OPTIMIZED OFFLINE MODE")
    print("=" * 60)
    print("✅ Internet:", "🌐 Connected" if check_internet() else "❌ Offline (OK)")
    print("🎤 Speech Recognition: Vosk (Optimized Offline)")
    print("🤖 AI Model: Ollama llama3.2:1b")
    print("⚡ Performance: Optimized for speed")
    print("=" * 60)
    print("💤 Myra is sleeping...")
    print("🗣️  Say 'Myra' or 'Hey Myra' to wake me up!")
    print("🛑 Press Ctrl+C to exit")
    
    # Start audio stream
    vosk_listener.start_stream()
    
    try:
        while True:
            if not is_awake:
                # Listen for wake word
                if vosk_listener.listen_for_wake_word():
                    is_awake = True
                    speak("Yes? How can I help you?")
                    
                    # Wait for command
                    command = vosk_listener.listen_for_command()
                    if command:
                        print(f"📝 Full command: {command}")
                        response = process_command(command)
                        speak(response)
                    else:
                        speak("I didn't catch that. Try again!")
                    
                    if is_awake:  # Stay awake for follow-up
                        speak("Anything else?")
                        follow_up = vosk_listener.listen_for_command(timeout=5)
                        if follow_up:
                            response = process_command(follow_up)
                            speak(response)
                    
                    is_awake = False  # Go back to sleep
                    print("💤 Going back to sleep...")
            
            time.sleep(0.05)  # Very small delay
            
    except KeyboardInterrupt:
        print("\n👋 Myra shutting down. Goodbye!")
        speak("Goodbye!")
    finally:
        vosk_listener.stop_stream()

if __name__ == "__main__":
    main()
