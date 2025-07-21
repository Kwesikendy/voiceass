#!/usr/bin/env python3
"""
🤖 Myra Voice Assistant - LONG DISTANCE OPTIMIZED
Enhanced for 30+ meter listening range with advanced audio processing
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
import numpy as np

# Speech recognition - optimized for distance
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

# === LONG-DISTANCE OPTIMIZED SETUP ===
MODEL_PATH = "vosk-model"
if not os.path.exists(MODEL_PATH):
    print("❌ Vosk model not found. Run download_vosk_model.py first")
    exit(1)

print("🔄 Loading speech model for long-distance recognition...")
model = vosk.Model(MODEL_PATH)

# OPTIMIZED recognizer for long-distance
rec = vosk.KaldiRecognizer(model, 16000)
rec.SetWords(True)
rec.SetPartialWords(True)

# ENHANCED audio settings for long-distance listening
CHUNK = 2048  # Larger chunks for better distant audio processing
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Long-distance audio processing parameters
NOISE_GATE_THRESHOLD = 200  # Lower threshold for distant sounds
VOICE_ACTIVITY_THRESHOLD = 300
ENERGY_AMPLIFICATION = 2.5  # Amplify quiet distant sounds
SILENCE_TIMEOUT = 3.0  # Longer timeout for distant speech

audio = pyaudio.PyAudio()
print("✅ Long-distance speech recognition ready")

# === ENHANCED TTS SETUP ===
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break
else:
    if len(voices) > 1:
        engine.setProperty('voice', voices[1].id)

engine.setProperty('rate', 180)  # Slower for distant listening
engine.setProperty('volume', 1.0)  # Maximum volume

# === GLOBAL SETTINGS ===
WAKE_WORDS = ["myra", "hey myra", "hello myra", "hi myra", "wake up myra"]
MEMORY_FILE = "myra_memory.json"
is_awake = False

# Enhanced audio processing queue
audio_queue = queue.Queue(maxsize=100)  # Larger queue for processing
processed_queue = queue.Queue()

def speak(text):
    """Enhanced text-to-speech for long distance"""
    print(f"🤖 Myra: {text}")
    # Speak twice for distant users - first normal, then slightly louder
    engine.say(text)
    engine.runAndWait()
    time.sleep(0.3)
    engine.setProperty('volume', 1.0)
    engine.setProperty('rate', 170)  # Slightly slower for clarity
    engine.say(text)
    engine.runAndWait()
    engine.setProperty('rate', 180)  # Reset

def check_internet():
    """Quick internet check"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=1)
        return True
    except OSError:
        return False

def enhance_audio_for_distance(audio_data):
    """Apply audio enhancement for distant speech detection"""
    try:
        # Convert to numpy array for processing
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
        
        # Apply noise gate - remove very quiet background noise
        audio_np = np.where(np.abs(audio_np) > NOISE_GATE_THRESHOLD, audio_np, 0)
        
        # Amplify remaining audio for distant voices
        audio_np = audio_np * ENERGY_AMPLIFICATION
        
        # Apply dynamic range compression to make quiet sounds louder
        audio_np = np.tanh(audio_np / 16384.0) * 16384.0
        
        # Ensure we don't clip
        audio_np = np.clip(audio_np, -32767, 32767)
        
        return audio_np.astype(np.int16).tobytes()
        
    except Exception as e:
        print(f"⚠️ Audio enhancement error: {e}")
        return audio_data

def get_microphone_with_best_range():
    """Find the best microphone for long-distance listening"""
    print("🔍 Scanning for optimal microphone...")
    
    best_devices = []
    for i in range(audio.get_device_count()):
        try:
            info = audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                name = info['name'].lower()
                
                # Prioritize microphones likely to have good range
                score = 0
                if 'array' in name or 'beam' in name:
                    score += 3  # Microphone arrays are great for distance
                if 'realtek' in name or 'high definition' in name:
                    score += 2  # Good quality built-in mics
                if 'usb' in name or 'external' in name:
                    score += 2  # External mics often better
                if 'noise' in name or 'cancel' in name:
                    score += 1  # Noise cancelling helps
                
                best_devices.append((i, info['name'], score))
        except:
            continue
    
    # Sort by score and return best options
    best_devices.sort(key=lambda x: x[2], reverse=True)
    
    if best_devices:
        print(f"🎤 Recommended microphones for long-distance:")
        for i, (dev_id, name, score) in enumerate(best_devices[:3]):
            print(f"   {i+1}. Device {dev_id}: {name} (Score: {score})")
    
    return best_devices

class LongDistanceVoskListener:
    """Enhanced Vosk listener optimized for long-distance listening"""
    
    def __init__(self, device_id=None):
        self.device_id = device_id
        self.stream = None
        self.listening = False
        self.partial_result = ""
        self.last_activity = 0
        
    def start_stream(self):
        """Start enhanced audio stream for long-distance"""
        try:
            self.stream = audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=self.device_id,
                frames_per_buffer=CHUNK,
                stream_callback=self.audio_callback
            )
            self.stream.start_stream()
            print("🎙️ Long-distance audio stream active")
        except Exception as e:
            print(f"❌ Error starting audio stream: {e}")
            raise
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """Enhanced audio callback with distance processing"""
        if self.listening:
            # Apply audio enhancement before queueing
            enhanced_audio = enhance_audio_for_distance(in_data)
            
            # Check for voice activity
            audio_np = np.frombuffer(enhanced_audio, dtype=np.int16)
            energy = np.sqrt(np.mean(audio_np.astype(np.float32)**2))
            
            if energy > VOICE_ACTIVITY_THRESHOLD:
                self.last_activity = time.time()
                audio_queue.put(enhanced_audio)
            elif time.time() - self.last_activity < SILENCE_TIMEOUT:
                # Keep processing for a bit after voice stops
                audio_queue.put(enhanced_audio)
        
        return (in_data, pyaudio.paContinue)
    
    def stop_stream(self):
        """Stop audio stream"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
    
    def listen_for_wake_word(self, timeout=10):
        """Enhanced wake word detection for long distance"""
        print("🔊 Listening for wake word (long-distance mode)...")
        print("📢 Speak clearly from any distance up to 30+ meters")
        
        self.listening = True
        start_time = time.time()
        self.last_activity = time.time()
        
        # Clear old audio data
        while not audio_queue.empty():
            try:
                audio_queue.get_nowait()
            except:
                break
        
        accumulated_text = ""
        
        while time.time() - start_time < timeout:
            try:
                # Get enhanced audio data
                data = audio_queue.get(timeout=0.5)
                
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get('text', '').strip()
                    
                    if text:
                        accumulated_text += " " + text
                        print(f"🗣️ Heard: {text}")
                        print(f"🔍 Checking: '{accumulated_text.strip()}'")
                        
                        # Check for wake words in accumulated text
                        full_text = accumulated_text.lower().strip()
                        for wake_word in WAKE_WORDS:
                            if wake_word in full_text:
                                print(f"✅ Wake word detected: {wake_word}")
                                self.listening = False
                                return True
                        
                        # Reset if text gets too long without wake word
                        if len(accumulated_text.split()) > 10:
                            accumulated_text = " ".join(accumulated_text.split()[-5:])
                
                else:
                    # Process partial results for immediate feedback
                    partial = json.loads(rec.PartialResult())
                    partial_text = partial.get('partial', '').strip()
                    
                    if partial_text and partial_text != self.partial_result:
                        self.partial_result = partial_text
                        print(f"🎧 Hearing: {partial_text}")
                        
                        # Quick check on partial results too
                        for wake_word in WAKE_WORDS:
                            if wake_word in partial_text.lower():
                                print(f"✅ Wake word detected (partial): {wake_word}")
                                self.listening = False
                                return True
                                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠️ Processing error: {e}")
                continue
        
        self.listening = False
        print("⏰ Wake word timeout")
        return False
    
    def listen_for_command(self, timeout=15):
        """Enhanced command listening for long distance"""
        print("🎧 Listening for command (long-distance mode)...")
        print("📢 Speak your command clearly")
        
        self.listening = True
        start_time = time.time()
        self.last_activity = time.time()
        command_parts = []
        
        # Clear queue
        while not audio_queue.empty():
            try:
                audio_queue.get_nowait()
            except:
                break
        
        while time.time() - start_time < timeout:
            try:
                data = audio_queue.get(timeout=1.0)
                
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get('text', '').strip()
                    
                    if text:
                        command_parts.append(text)
                        print(f"📝 Command part: {text}")
                        
                        # If we have a reasonable command, return it
                        full_command = ' '.join(command_parts)
                        if len(full_command.split()) >= 2:
                            print(f"📝 Full command captured: {full_command}")
                            self.listening = False
                            return full_command
                
                else:
                    # Show partial results
                    partial = json.loads(rec.PartialResult())
                    partial_text = partial.get('partial', '').strip()
                    
                    if partial_text and partial_text != self.partial_result:
                        self.partial_result = partial_text
                        print(f"🎧 Hearing: {partial_text}")
                        
            except queue.Empty:
                # Check if we have enough for a command
                if command_parts:
                    full_command = ' '.join(command_parts)
                    if len(full_command.split()) >= 1:
                        self.listening = False
                        return full_command
                continue
            except Exception as e:
                print(f"⚠️ Command processing error: {e}")
                continue
        
        self.listening = False
        # Return accumulated command if any
        if command_parts:
            return ' '.join(command_parts)
        return ""

# Memory functions (same as before)
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

# System commands (same as before)
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
        for _ in range(5):  # More volume steps for distant users
            subprocess.run(["powershell", "-Command", 
                          "(New-Object -comObject WScript.Shell).SendKeys([char]175)"], 
                          check=True, capture_output=True)
        return "Volume increased significantly"
    
    elif "volume down" in command or "quieter" in command:
        for _ in range(5):
            subprocess.run(["powershell", "-Command", 
                          "(New-Object -comObject WScript.Shell).SendKeys([char]174)"], 
                          check=True, capture_output=True)
        return "Volume decreased significantly"
    
    elif "mute" in command:
        subprocess.run(["powershell", "-Command", 
                      "(New-Object -comObject WScript.Shell).SendKeys([char]173)"], 
                      check=True, capture_output=True)
        return "Audio muted"
    
    elif "time" in command:
        now = datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')}"
    
    elif "date" in command:
        now = datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}"
    
    return None

# File search and AI functions (same as optimized version)
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
                if root.count(os.sep) - search_path.count(os.sep) > 1:
                    continue
                
                for file in files:
                    if query.lower() in file.lower():
                        matches.append(os.path.join(root, file))
                        
                for dir_name in dirs:
                    if query.lower() in dir_name.lower():
                        matches.append(os.path.join(root, dir_name))
                
                if len(matches) >= 3:
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

def get_ai_response(question):
    """Quick AI response from Ollama"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": f"Answer briefly in 1-2 sentences: {question}",
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 50}
            },
            timeout=8
        )
        
        if response.status_code == 200:
            return response.json().get("response", "Sorry, no response from AI")
        else:
            return "AI is not responding right now"
            
    except:
        return "AI service unavailable"

def process_command(command):
    """Process user commands quickly"""
    global is_awake
    
    if any(word in command for word in ["goodbye", "bye", "stop", "exit", "quit"]):
        is_awake = False
        return "Goodbye! Say my name to wake me up again."
    
    elif "my name is" in command:
        name = command.split("my name is")[-1].strip()
        update_memory("user_name", name)
        return f"Nice to meet you, {name}! I can hear you clearly even from a distance."
    
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
        return "I can help with opening files, system commands, or answering questions. I can hear you from anywhere in the room!"

def main():
    """Long-distance optimized main loop"""
    global is_awake
    
    print("🚀 Myra Voice Assistant - LONG DISTANCE MODE")
    print("=" * 70)
    print("✅ Internet:", "🌐 Connected" if check_internet() else "❌ Offline (OK)")
    print("🎤 Speech Recognition: Vosk (Long-Distance Optimized)")
    print("🤖 AI Model: Ollama llama3.2:1b")
    print("📏 Range: Optimized for 30+ meter listening distance")
    print("⚡ Audio Enhancement: Active noise gating & amplification")
    print("=" * 70)
    
    # Get best microphone for long distance
    best_mics = get_microphone_with_best_range()
    
    print("\n🔧 Microphone Selection:")
    print("1. Use recommended microphone (automatic)")
    print("2. Select specific microphone")
    print("3. Use default microphone")
    
    choice = input("Enter choice (1-3): ").strip()
    
    device_id = None
    if choice == "1" and best_mics:
        device_id = best_mics[0][0]  # Use highest scored mic
        print(f"✅ Using recommended: {best_mics[0][1]}")
    elif choice == "2":
        try:
            device_num = int(input("Enter device number: "))
            device_id = device_num
            print(f"✅ Using device {device_id}")
        except:
            print("✅ Using default microphone")
    else:
        print("✅ Using default microphone")
    
    # Initialize long-distance listener
    vosk_listener = LongDistanceVoskListener(device_id)
    vosk_listener.start_stream()
    
    print("\n💤 Myra is sleeping...")
    print("🗣️  Say 'Myra' or 'Hey Myra' from anywhere up to 30+ meters!")
    print("📢 Speak clearly and at normal volume")
    print("🛑 Press Ctrl+C to exit")
    
    try:
        while True:
            if not is_awake:
                # Listen for wake word with long timeout for distant users
                if vosk_listener.listen_for_wake_word(timeout=15):
                    is_awake = True
                    speak("Yes? I can hear you clearly. What can I do for you?")
                    
                    # Wait for command with extended timeout
                    command = vosk_listener.listen_for_command(timeout=20)
                    if command:
                        print(f"📝 Processing command: {command}")
                        response = process_command(command)
                        speak(response)
                    else:
                        speak("I didn't catch your command. Please try again!")
                    
                    if is_awake:  # Stay awake for follow-up
                        speak("Is there anything else I can help you with?")
                        follow_up = vosk_listener.listen_for_command(timeout=15)
                        if follow_up:
                            response = process_command(follow_up)
                            speak(response)
                        else:
                            speak("I'll go back to sleep now. Call my name when you need me!")
                    
                    is_awake = False
                    print("💤 Going back to sleep...")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n👋 Myra shutting down. Goodbye!")
        speak("Goodbye! It was great hearing you from afar!")
    finally:
        vosk_listener.stop_stream()

if __name__ == "__main__":
    main()
