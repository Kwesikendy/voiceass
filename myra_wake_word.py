import speech_recognition as sr
import pyttsx3
import requests
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

# === Setup ===
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Configure voice to be female
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
        print(f"🎤 Using default voice: {voices[0].name if voices else 'Unknown'}")

# Set speech rate and volume
engine.setProperty('rate', 180)
engine.setProperty('volume', 0.9)

OLLAMA_URL = "http://localhost:11434/api/generate"

# Wake words that will activate Myra
WAKE_WORDS = ["hello myra", "hey myra", "hi myra", "myra", "okay myra"]

# Configure recognizer for better sensitivity (lower threshold = more sensitive)
recognizer.energy_threshold = 100  # Much lower for better sensitivity
recognizer.dynamic_energy_threshold = True
recognizer.dynamic_energy_adjustment_damping = 0.1  # More responsive to changes
recognizer.dynamic_energy_ratio = 1.2  # More sensitive ratio
recognizer.pause_threshold = 0.5  # Shorter pause before considering speech ended

# Global flag to control listening state
listening_active = False

def get_available_models():
    """Get list of available Ollama models"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
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
        print("❌ No Ollama models found. Please install one first:")
        print("  ollama pull llama3.2:1b")
        return None
    
    preferred_models = [
        'llama3.2:3b', 'llama3.2:1b', 'llama3.1:8b', 'llama3.1:7b',
        'mistral:7b', 'mistral:latest', 'gemma:7b', 'codellama:7b'
    ]
    
    for preferred in preferred_models:
        if preferred in models:
            print(f"✅ Using model: {preferred}")
            return preferred
    
    selected = models[0]
    print(f"✅ Using model: {selected}")
    return selected

MODEL_NAME = select_model()

def check_wake_word(command):
    """Check if wake word is detected with fuzzy matching"""
    command_lower = command.lower()
    
    # Direct matches
    if any(wake_word in command_lower for wake_word in WAKE_WORDS):
        return True
        
    # Handle common misrecognitions
    misrecognitions = {
        "mirror": "myra",
        "maria": "myra", 
        "mira": "myra",
        "maya": "myra",
        "hello maria": "hello myra",
        "hey maria": "hey myra",
        "hi maria": "hi myra",
        "hello mirror": "hello myra",
        "hey mirror": "hey myra",
        "hi mirror": "hi myra",
        "hello mira": "hello myra",
        "hey mira": "hey myra",
        "hi mira": "hi myra"
    }
    
    # Check for misrecognitions
    for misrecognition, correct in misrecognitions.items():
        if misrecognition in command_lower:
            print(f"🔧 Corrected '{misrecognition}' to '{correct}'")
            return True
            
    return False

def speak(text):
    """Text to speech function"""
    print("Myra:", text)
    engine.say(text)
    engine.runAndWait()

def listen_for_wake_word():
    """Continuously listen for wake word in the background"""
    global listening_active
    
    with sr.Microphone() as source:
        print("📡 Calibrating microphone for better sensitivity...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Shorter calibration
    
    print("🔊 Myra is sleeping. Say 'Hello Myra' to wake me up...")
    
    while True:
        if listening_active:
            time.sleep(0.1)  # Wait while active session is running
            continue
            
        try:
            with sr.Microphone() as source:
                # Listen with shorter timeout for wake word detection
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=3)
            
            try:
                command = recognizer.recognize_google(audio).lower()
                print(f"🔍 Heard: {command}")
                
                # Check if any wake word is detected (with fuzzy matching)
                if check_wake_word(command):
                    print("🚀 Wake word detected! Activating Myra...")
                    listening_active = True
                    activate_myra()
                    
            except sr.UnknownValueError:
                # Ignore unrecognized speech when waiting for wake word
                pass
            except sr.RequestError:
                print("❌ Speech service temporarily unavailable")
                time.sleep(5)
                
        except sr.WaitTimeoutError:
            # Normal timeout, continue listening
            pass
        except Exception as e:
            print(f"❌ Error in wake word detection: {e}")
            time.sleep(1)

def listen_active():
    """Listen for commands when Myra is active"""
    with sr.Microphone() as source:
        print("👂 Listening...")
        try:
            # Quick ambient noise adjustment for active listening
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=7)
        except sr.WaitTimeoutError:
            return ""

    try:
        command = recognizer.recognize_google(audio)
        print(f"You: {command}")
        return command
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError as e:
        speak("Sorry, speech service is down.")
        return ""

def adjust_brightness(action):
    """Adjust screen brightness with intelligent word recognition"""
    try:
        action_lower = action.lower()
        
        # Words that mean make it brighter
        increase_words = [
            "increase", "up", "higher", "brighter", "bright", "more", 
            "raise", "turn up", "boost", "enhance", "amplify", "max", "maximum"
        ]
        
        # Words that mean make it darker/dimmer
        decrease_words = [
            "decrease", "down", "lower", "darker", "dark", "less", "dim", 
            "reduce", "turn down", "minimize", "min", "minimum", "lessen"
        ]
        
        # Check for specific percentage values
        import re
        percentage_match = re.search(r'(\d+)\s*(?:percent|%)?', action_lower)
        
        if percentage_match:
            percentage = int(percentage_match.group(1))
            # Ensure percentage is within valid range
            percentage = max(10, min(100, percentage))
            subprocess.run(["powershell", "-Command", 
                          f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {percentage})"], 
                          check=True, capture_output=True)
            return f"Brightness set to {percentage} percent."
        
        # Check for increase commands
        elif any(word in action_lower for word in increase_words):
            subprocess.run(["powershell", "-Command", 
                          "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, 100)"], 
                          check=True, capture_output=True)
            return "Brightness increased to maximum."
        
        # Check for decrease commands (this was the bug!)
        elif any(word in action_lower for word in decrease_words):
            subprocess.run(["powershell", "-Command", 
                          "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, 30)"], 
                          check=True, capture_output=True)
            return "Brightness decreased to 30 percent."
        
        elif "brightness" in action_lower:
            if any(word in action_lower for word in ["change", "adjust", "set", "modify"]):
                return "Would you like me to make the screen brighter or darker?"
            else:
                return "Should I make the screen brighter or darker?"
        
        else:
            return "I can make your screen brighter or darker. What would you prefer?"
            
    except Exception as e:
        return "Sorry, I couldn't adjust the brightness. This might require administrator privileges."

def search_files(query):
    """Search for folders or files if Myra doesn't recognize something"""
    try:
        matches = []
        # Searching in current directory and common locations
        search_paths = ['.', os.path.expanduser('~'), 'C:\\Users']
        
        for search_path in search_paths:
            if os.path.exists(search_path):
                for root, dirnames, filenames in os.walk(search_path):
                    # Limit search depth to avoid taking too long
                    if root.count(os.sep) - search_path.count(os.sep) > 3:
                        continue
                    
                    for filename in fnmatch.filter(filenames, f'*{query}*'):
                        matches.append(os.path.join(root, filename))
                    for dirname in fnmatch.filter(dirnames, f'*{query}*'):
                        matches.append(os.path.join(root, dirname))
                    
                    # Limit results to avoid overwhelming
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
    """Open a file or folder using the default system application"""
    try:
        if os.path.isdir(path):
            # It's a folder - open in file explorer
            os.startfile(path)
            speak(f"Opened folder: {os.path.basename(path)}")
        else:
            # It's a file - open with default application
            os.startfile(path)
            speak(f"Opened file: {os.path.basename(path)}")
    except Exception as e:
        speak("Sorry, I couldn't open that file or folder.")
        print(f"Error opening {path}: {e}")


def control_system(command):
    """Handle all system control commands"""
    command_lower = command.lower()
    
    # Shutdown commands
    if any(x in command_lower for x in ["shutdown", "turn off", "power off"]):
        speak("Shutting down the computer in 10 seconds. Say cancel to stop.")
        time.sleep(3)
        speak("Shutting down now.")
        try:
            os.system("shutdown /s /t 5")
            return "Computer is shutting down."
        except:
            return "Sorry, I couldn't shut down the computer."
    
    # Restart commands
    elif any(x in command_lower for x in ["restart", "reboot"]):
        speak("Restarting the computer in 10 seconds. Say cancel to stop.")
        time.sleep(3)
        speak("Restarting now.")
        try:
            os.system("shutdown /r /t 5")
            return "Computer is restarting."
        except:
            return "Sorry, I couldn't restart the computer."
    
    # Lock screen
    elif any(x in command_lower for x in ["lock", "lock screen", "lock computer"]):
        try:
            os.system("rundll32.exe user32.dll, LockWorkStation")
            return "Screen locked."
        except:
            return "Sorry, I couldn't lock the screen."
    
    # Sleep/hibernate
    elif any(x in command_lower for x in ["sleep", "hibernate"]):
        try:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "Computer is going to sleep."
        except:
            return "Sorry, I couldn't put the computer to sleep."
    
    # Brightness controls
    elif any(x in command_lower for x in ["brightness", "screen brightness"]) or any(word in command_lower for word in ["brighter", "darker", "dim", "reduce brightness", "increase brightness"]):
        return adjust_brightness(command_lower)
    
    # Volume controls
    elif "volume" in command_lower or "sound" in command_lower or "audio" in command_lower:
        volume_up_words = ["up", "increase", "higher", "raise", "boost", "more", "louder", "turn up"]
        volume_down_words = ["down", "decrease", "lower", "reduce", "less", "quieter", "turn down", "softer"]
        mute_words = ["mute", "silence", "quiet", "off", "shut up"]
        
        # Check for specific percentage values in volume commands
        import re
        volume_percentage_match = re.search(r'(\d+)\s*(?:percent|%)?', command_lower)
        
        try:
            if volume_percentage_match:
                percentage = int(volume_percentage_match.group(1))
                percentage = max(0, min(100, percentage))  # Ensure 0-100 range
                # Use nircmd for precise volume control (if available) or approximate with key presses
                volume_level = int((percentage / 100) * 65535)  # Convert to Windows volume scale
                powershell_cmd = f"""(New-Object -comObject WScript.Shell).SendKeys([char]175)"""
                # Alternative: Use Windows API directly
                subprocess.run(["powershell", "-Command", 
                              f"Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Win32 {{ [DllImport(\"user32.dll\")] public static extern IntPtr SendMessageW(IntPtr hWnd, int Msg, IntPtr wParam, IntPtr lParam); }}'; [Win32]::SendMessageW(-1, 0x319, 0, {volume_level})"], 
                              check=True, capture_output=True)
                return f"Volume set to {percentage} percent."
            elif any(word in command_lower for word in mute_words):
                # Use VK_VOLUME_MUTE (0xAD)
                subprocess.run(["powershell", "-Command", 
                              "(New-Object -comObject WScript.Shell).SendKeys([char]173)"], 
                              check=True, capture_output=True)
                return "Audio muted."
            elif any(word in command_lower for word in volume_up_words):
                # Use VK_VOLUME_UP (0xAF) - send multiple times for noticeable change
                for _ in range(5):
                    subprocess.run(["powershell", "-Command", 
                                  "(New-Object -comObject WScript.Shell).SendKeys([char]175)"], 
                                  check=True, capture_output=True)
                    time.sleep(0.1)
                return "Volume increased."
            elif any(word in command_lower for word in volume_down_words):
                # Use VK_VOLUME_DOWN (0xAE) - send multiple times for noticeable change
                for _ in range(5):
                    subprocess.run(["powershell", "-Command", 
                                  "(New-Object -comObject WScript.Shell).SendKeys([char]174)"], 
                                  check=True, capture_output=True)
                    time.sleep(0.1)
                return "Volume decreased."
            else:
                return "Would you like me to turn the volume up, down, or mute it?"
        except Exception as e:
            return "Sorry, I couldn't adjust the volume."
    
    # Application management
    elif any(x in command_lower for x in ["calculator", "notepad", "word", "excel", "powerpoint", "chrome", "firefox", "edge"]):
        app_mapping = {
            "calculator": "calc", "notepad": "notepad", "word": "winword", 
            "excel": "excel", "powerpoint": "powerpnt", 
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
    
    # Music playback
    elif "play music" in command_lower or "play song" in command_lower:
        song = command_lower.replace("play music ", "").replace("play song ", "").replace("play ", "")
        try:
            if song:
                search_url = f"https://www.youtube.com/results?search_query={song.replace(' ', '+')}"
                webbrowser.open(search_url)
                return f"Opening YouTube to play {song}."
            else:
                os.system("start mswindowsstore://pdp/?ProductId=9WZDNCRFJ3PT")
                return "Opening music player."
        except:
            return "Sorry, I couldn't play music."
    
    # Web browsing
    elif "search" in command_lower or "google" in command_lower:
        query = command_lower.replace("search ", "").replace("google ", "")
        if query:
            webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            return f"Searching for {query} in your browser."
        else:
            webbrowser.open("https://www.google.com")
            return "Opening Google."
    
    # Screenshot
    elif "screenshot" in command_lower or "capture screen" in command_lower:
        try:
            screenshot = pyautogui.screenshot()
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot.save(filename)
            return f"Screenshot saved as {filename}."
        except:
            return "Sorry, I couldn't take a screenshot."
    
    # System information
    elif "system info" in command_lower or "pc info" in command_lower:
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:\\')
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
    
    # Weather
    elif "weather" in command_lower:
        try:
            webbrowser.open("https://weather.com")
            return "Opening weather information."
        except:
            return "Sorry, I couldn't open weather information."
    
    # News
    elif "news" in command_lower:
        try:
            webbrowser.open("https://news.google.com")
            return "Opening latest news."
        except:
            return "Sorry, I couldn't open news."
    
    # Cancel shutdown/restart
    elif "cancel" in command_lower:
        try:
            os.system("shutdown /a")
            return "Shutdown cancelled."
        except:
            return "No shutdown to cancel."
    
    return None

def ask_ollama(prompt):
    """Get AI response from Ollama"""
    if not MODEL_NAME:
        return "Sorry, no AI model is available."
    
    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": True
        }
        response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=30)
        
        if response.status_code != 200:
            return f"Error: Ollama returned status {response.status_code}"
        
        reply = ""
        print("Myra: ", end="", flush=True)
        
        for line in response.iter_lines():
            if line:
                data = line.decode('utf-8')
                try:
                    if data.startswith('{') and 'response' in data:
                        json_data = json.loads(data)
                        text = json_data.get('response', '')
                        print(text, end='', flush=True)
                        reply += text
                        
                        if json_data.get('done', False):
                            break
                except json.JSONDecodeError:
                    continue
        
        print()
        return reply.strip()
        
    except requests.exceptions.Timeout:
        return "Sorry, the AI model is taking too long to respond."
    except requests.exceptions.ConnectionError:
        return "Sorry, I can't connect to the AI service. Is Ollama running?"
    except Exception as e:
        return f"Sorry, there was an error: {str(e)}"

def give_feedback():
    """Provide user with real-time status updates"""
    feedback_options = [
        "Could you wait a while as I try to fulfill your request?",
        "Please give me a sec, I'm coming.",
        "Hang tight, just processing your request now.",
        "I'm working on it, one moment please.",
    ]
    speak(random.choice(feedback_options))


def activate_myra():
    """Main active session when Myra is awakened"""
    global listening_active
    
    speak("Hi! I'm awake. How can I help you?")
    
    inactive_count = 0  # Track consecutive inactive cycles
    
    while listening_active:
        query = listen_active()
        
        if query == "":
            inactive_count += 1
            if inactive_count >= 3:  # Go back to sleep after 3 empty responses
                speak("I'll go back to sleep now. Say 'Hello Myra' to wake me up again.")
                listening_active = False
                break
            continue
        
        inactive_count = 0  # Reset counter on successful input
        
        # Check for sleep commands
        if any(x in query.lower() for x in ["go to sleep", "sleep now", "that's all", "goodbye myra"]):
            speak("Going back to sleep. Say 'Hello Myra' to wake me up again.")
            listening_active = False
            break
        
        # Special commands
        if "what's your name" in query.lower() or "who are you" in query.lower():
            speak("I am Myra, your AI voice assistant!")
            continue
        
        if "what can you do" in query.lower():
            speak("I can control your computer, open apps, play music, search the web, take screenshots, tell you the time, weather, news, and answer any questions you have. What would you like me to do?")
            continue
        
        # Check for system control commands first
        system_response = control_system(query)
        if system_response:
            speak(system_response)
            continue
        
        # Search for folders/files if the command isn't recognized and contains "open"
        if "open" in query.lower():
            # Extract the thing they want to open
            search_term = query.lower().replace("open", "").strip()
            if search_term:
                give_feedback()  # Let them know we're working on it
                found_items = search_files(search_term)
                if found_items:
                    continue

        # Get AI response for general questions
        answer = ask_ollama(query)
        if answer:
            speak(answer)

def main():
    """Main function"""
    if not MODEL_NAME:
        print("❌ No AI models available. Please install one first.")
        return
    
    print("🤖 Myra Voice Assistant with Wake Word Activation")
    print("💤 Myra is sleeping...")
    print("🗣️  Wake words: 'Hello Myra', 'Hey Myra', 'Hi Myra'")
    print("🛑 To stop completely, use Ctrl+C")
    
    try:
        # Start wake word detection in main thread
        listen_for_wake_word()
    except KeyboardInterrupt:
        print("\n👋 Myra is shutting down. Goodbye!")

if __name__ == "__main__":
    main()
