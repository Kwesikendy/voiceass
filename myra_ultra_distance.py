#!/usr/bin/env python3
"""
🤖 Myra Voice Assistant - ULTRA DISTANCE OPTIMIZED
Advanced distant speech correction with fuzzy matching and phonetic analysis
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
import difflib
import re

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

# === ULTRA-DISTANCE OPTIMIZED SETUP ===
MODEL_PATH = "vosk-model"
if not os.path.exists(MODEL_PATH):
    print("❌ Vosk model not found. Run download_vosk_model.py first")
    exit(1)

print("🔄 Loading ultra-optimized speech model...")
model = vosk.Model(MODEL_PATH)

# ENHANCED recognizer for ultra-distance
rec = vosk.KaldiRecognizer(model, 16000)
rec.SetWords(True)
rec.SetPartialWords(True)

# ULTRA-ENHANCED audio settings
CHUNK = 4096  # Even larger chunks for better processing
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Ultra-distance audio processing parameters
NOISE_GATE_THRESHOLD = 150  # Even lower threshold
VOICE_ACTIVITY_THRESHOLD = 250
ENERGY_AMPLIFICATION = 3.5  # Higher amplification
SILENCE_TIMEOUT = 4.0
PRE_EMPHASIS = 0.97  # Audio pre-emphasis filter

audio = pyaudio.PyAudio()
print("✅ Ultra-distance speech recognition ready")

# === FUZZY WAKE WORD MATCHING ===
WAKE_WORDS = ["myra", "hey myra", "hello myra", "hi myra", "wake up myra"]

# Common misheard variations of "myra" at distance
MYRA_VARIATIONS = [
    "myra", "mira", "moira", "maya", "maria", "mya", "mira", 
    "murh", "murph", "mur", "my", "mir", "more", "mar",
    "europe", "euro", "your", "you", "yura", "yara",
    "ira", "era", "ara", "ora", "ura", "ira",
    "mya", "nya", "rya", "lya", "dya",
    "mara", "mora", "mura", "mira", "mera"
]

HEY_MYRA_VARIATIONS = [
    "hey myra", "hey mira", "hey maria", "hey maya", "hey moira",
    "hey murph", "hey europe", "hey your", "hey you",
    "a myra", "a mira", "hey my", "hey mir", "hey mar",
    "hey more", "hey mur", "hey er", "hey are"
]

ALL_WAKE_PATTERNS = MYRA_VARIATIONS + HEY_MYRA_VARIATIONS

def calculate_similarity(text1, text2):
    """Calculate similarity between two strings"""
    return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def phonetic_similarity(word1, word2):
    """Simple phonetic similarity check"""
    # Remove common consonant confusions at distance
    def normalize_phonetic(word):
        word = word.lower()
        # Common distant speech issues
        word = word.replace('ph', 'f')
        word = word.replace('europe', 'myra')  # Direct mapping for common mishearing
        word = word.replace('murph', 'myra')   # Direct mapping
        word = word.replace('mur', 'myr')
        word = word.replace('eur', 'myr')
        word = word.replace('ur', 'yr')
        # Remove ending consonants that get lost at distance
        if word.endswith(('h', 'p', 'k', 't')):
            word = word[:-1]
        return word
    
    norm1 = normalize_phonetic(word1)
    norm2 = normalize_phonetic(word2)
    
    return calculate_similarity(norm1, norm2)

def is_wake_word_fuzzy(text):
    """Enhanced fuzzy wake word detection"""
    text = text.lower().strip()
    
    # Direct exact matches first
    for wake_word in WAKE_WORDS:
        if wake_word in text:
            return True, wake_word, 1.0
    
    # Check for direct variations
    for variation in ALL_WAKE_PATTERNS:
        if variation in text:
            return True, f"myra (heard as '{variation}')", 0.9
    
    # Fuzzy matching with similarity threshold
    words = text.split()
    for word in words:
        # Check similarity to "myra"
        similarity = calculate_similarity(word, "myra")
        if similarity >= 0.6:  # 60% similarity threshold
            return True, f"myra (heard as '{word}', {similarity:.1%} match)", similarity
        
        # Check phonetic similarity
        phonetic_sim = phonetic_similarity(word, "myra")
        if phonetic_sim >= 0.7:  # 70% phonetic similarity
            return True, f"myra (phonetic match '{word}', {phonetic_sim:.1%})", phonetic_sim
    
    # Check multi-word patterns
    if len(words) >= 2:
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            for wake_phrase in ["hey myra", "hello myra", "hi myra"]:
                if calculate_similarity(phrase, wake_phrase) >= 0.6:
                    return True, f"{wake_phrase} (heard as '{phrase}')", 0.8
    
    return False, "", 0.0

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

engine.setProperty('rate', 170)  # Slower for distant listening
engine.setProperty('volume', 1.0)

# === GLOBAL SETTINGS ===
MEMORY_FILE = "myra_memory.json"
is_awake = False

# Ultra-enhanced audio processing queue
audio_queue = queue.Queue(maxsize=200)  # Even larger queue

def speak(text):
    """Simple text-to-speech to avoid threading issues"""
    print(f"🤖 Myra: {text}")
    try:
        engine.say(text)
        engine.runAndWait()
    except:
        # If TTS fails, at least print the response
        print(f"[TTS Error - Message: {text}]")

def check_internet():
    """Quick internet check"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=1)
        return True
    except OSError:
        return False

def apply_pre_emphasis(audio_data):
    """Apply pre-emphasis filter to enhance speech intelligibility"""
    try:
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
        
        # Pre-emphasis filter to boost high frequencies (speech clarity)
        emphasized = np.append(audio_np[0], audio_np[1:] - PRE_EMPHASIS * audio_np[:-1])
        
        return emphasized
    except:
        return np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)

def enhance_audio_ultra_distance(audio_data):
    """Ultra-enhanced audio processing for maximum distance"""
    try:
        # Apply pre-emphasis first
        audio_np = apply_pre_emphasis(audio_data)
        
        # Aggressive noise gate
        audio_np = np.where(np.abs(audio_np) > NOISE_GATE_THRESHOLD, audio_np, 0)
        
        # High amplification for distant speech
        audio_np = audio_np * ENERGY_AMPLIFICATION
        
        # Dynamic range compression with soft limiting
        audio_np = np.tanh(audio_np / 10000.0) * 10000.0
        
        # Spectral enhancement (simple high-pass filtering)
        # This helps with speech intelligibility at distance
        if len(audio_np) > 1:
            # Simple high-pass filter
            alpha = 0.95
            filtered = np.zeros_like(audio_np)
            filtered[0] = audio_np[0]
            for i in range(1, len(audio_np)):
                filtered[i] = alpha * filtered[i-1] + alpha * (audio_np[i] - audio_np[i-1])
            audio_np = filtered
        
        # Final clipping protection
        audio_np = np.clip(audio_np, -32767, 32767)
        
        return audio_np.astype(np.int16).tobytes()
        
    except Exception as e:
        print(f"⚠️ Audio enhancement error: {e}")
        return audio_data

class UltraDistanceVoskListener:
    """Ultra-enhanced Vosk listener with advanced distant speech processing"""
    
    def __init__(self, device_id=None):
        self.device_id = device_id
        self.stream = None
        self.listening = False
        self.partial_result = ""
        self.last_activity = 0
        self.wake_word_buffer = []  # Buffer for wake word analysis
        
    def start_stream(self):
        """Start ultra-enhanced audio stream"""
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
            print("🎙️ Ultra-distance audio stream active")
        except Exception as e:
            print(f"❌ Error starting audio stream: {e}")
            raise
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """Ultra-enhanced audio callback"""
        if self.listening:
            # Apply ultra-enhancement
            enhanced_audio = enhance_audio_ultra_distance(in_data)
            
            # Voice activity detection with lower threshold
            audio_np = np.frombuffer(enhanced_audio, dtype=np.int16)
            energy = np.sqrt(np.mean(audio_np.astype(np.float32)**2))
            
            if energy > VOICE_ACTIVITY_THRESHOLD:
                self.last_activity = time.time()
                audio_queue.put(enhanced_audio)
            elif time.time() - self.last_activity < SILENCE_TIMEOUT:
                audio_queue.put(enhanced_audio)
        
        return (in_data, pyaudio.paContinue)
    
    def stop_stream(self):
        """Stop audio stream"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
    
    def listen_for_wake_word(self, timeout=20):
        """Ultra-enhanced wake word detection with fuzzy matching"""
        print("🔊 Listening for wake word (ULTRA-DISTANCE mode)...")
        print("📢 Say 'MYRA' clearly - advanced speech correction active")
        
        self.listening = True
        start_time = time.time()
        self.last_activity = time.time()
        self.wake_word_buffer = []
        
        # Clear old audio data
        while not audio_queue.empty():
            try:
                audio_queue.get_nowait()
            except:
                break
        
        accumulated_text = ""
        recent_words = []  # Keep track of recent words for pattern matching
        
        while time.time() - start_time < timeout:
            try:
                data = audio_queue.get(timeout=0.3)
                
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get('text', '').strip()
                    
                    if text:
                        recent_words.extend(text.split())
                        # Keep only last 10 words to prevent memory buildup
                        recent_words = recent_words[-10:]
                        
                        accumulated_text = " ".join(recent_words)
                        
                        print(f"🗣️ Heard: '{text}'")
                        print(f"🔍 Analyzing: '{accumulated_text}'")
                        
                        # Advanced fuzzy wake word detection
                        is_wake, detected_word, confidence = is_wake_word_fuzzy(accumulated_text)
                        
                        if is_wake:
                            print(f"✅ WAKE WORD DETECTED: {detected_word} (confidence: {confidence:.1%})")
                            self.listening = False
                            return True
                        
                        # Also check just the latest word
                        is_wake_single, detected_single, conf_single = is_wake_word_fuzzy(text)
                        if is_wake_single:
                            print(f"✅ WAKE WORD DETECTED: {detected_single} (confidence: {conf_single:.1%})")
                            self.listening = False
                            return True
                
                else:
                    # Enhanced partial result processing
                    partial = json.loads(rec.PartialResult())
                    partial_text = partial.get('partial', '').strip()
                    
                    if partial_text and partial_text != self.partial_result:
                        self.partial_result = partial_text
                        print(f"🎧 Partial: '{partial_text}'")
                        
                        # Check partial results with fuzzy matching too
                        is_wake_partial, detected_partial, conf_partial = is_wake_word_fuzzy(partial_text)
                        if is_wake_partial and conf_partial > 0.8:  # Higher threshold for partials
                            print(f"✅ WAKE WORD DETECTED (partial): {detected_partial}")
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
        """Enhanced command listening"""
        print("🎧 Listening for command...")
        
        self.listening = True
        start_time = time.time()
        command_parts = []
        
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
                        
                        full_command = ' '.join(command_parts)
                        if len(full_command.split()) >= 2:
                            self.listening = False
                            return full_command
                
                else:
                    partial = json.loads(rec.PartialResult())
                    partial_text = partial.get('partial', '').strip()
                    
                    if partial_text and partial_text != self.partial_result:
                        self.partial_result = partial_text
                        print(f"🎧 Hearing: {partial_text}")
                        
            except queue.Empty:
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
        if command_parts:
            return ' '.join(command_parts)
        return ""

# Memory and system functions (same as before but simplified)
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def handle_system_command(command):
    """Handle system commands"""
    if "calculator" in command or "calc" in command:
        os.system("calc")
        return "Opening calculator"
    elif "notepad" in command:
        os.system("notepad")
        return "Opening notepad"
    elif "time" in command:
        now = datetime.now()
        return f"It's {now.strftime('%I:%M %p')}"
    elif "volume up" in command:
        for _ in range(5):
            subprocess.run(["powershell", "-Command", 
                          "(New-Object -comObject WScript.Shell).SendKeys([char]175)"], 
                          check=True, capture_output=True)
        return "Volume increased"
    return None

def process_command(command):
    """Process commands"""
    global is_awake
    
    if any(word in command for word in ["goodbye", "bye", "stop"]):
        is_awake = False
        return "Goodbye!"
    
    elif "my name is" in command:
        name = command.split("my name is")[-1].strip()
        return f"Nice to meet you, {name}!"
    
    elif "open" in command:
        return "I heard your open command!"
    
    system_response = handle_system_command(command)
    if system_response:
        return system_response
    
    return "I can help with system commands and more!"

def main():
    """Ultra-distance optimized main loop"""
    global is_awake
    
    print("🚀 Myra Voice Assistant - ULTRA DISTANCE MODE")
    print("=" * 70)
    print("🎤 Speech Recognition: Ultra-Enhanced Vosk")
    print("🧠 Wake Word Detection: Advanced Fuzzy Matching")
    print("📏 Range: Maximum distance with speech correction")
    print("⚡ Features: Pre-emphasis, noise gate, phonetic matching")
    print("=" * 70)
    
    # Use best microphone automatically
    best_device = None
    try:
        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0 and 'array' in info['name'].lower():
                best_device = i
                print(f"✅ Using: {info['name']}")
                break
    except:
        pass
    
    if not best_device:
        print("✅ Using default microphone")
    
    vosk_listener = UltraDistanceVoskListener(best_device)
    vosk_listener.start_stream()
    
    print("\n💤 Myra is sleeping...")
    print("🗣️  Say 'MYRA' from any distance - advanced correction active!")
    print("🔧 Will detect: myra, mira, murph, europe, and other variations")
    print("🛑 Press Ctrl+C to exit")
    
    try:
        while True:
            if not is_awake:
                if vosk_listener.listen_for_wake_word(timeout=30):  # Longer timeout
                    is_awake = True
                    speak("Yes, I heard you! What can I do?")
                    
                    command = vosk_listener.listen_for_command()
                    if command:
                        print(f"📝 Processing: {command}")
                        response = process_command(command)
                        speak(response)
                    else:
                        speak("I didn't catch that command.")
                    
                    is_awake = False
                    print("💤 Going back to sleep...")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        speak("Goodbye!")
    finally:
        vosk_listener.stop_stream()

if __name__ == "__main__":
    main()
