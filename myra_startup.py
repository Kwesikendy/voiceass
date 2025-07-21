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
import getpass

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

# Global flag to control listening state
listening_active = False
startup_greeting_done = False

def get_username():
    """Get the current system username"""
    try:
        return getpass.getuser()
    except:
        return "there"

def get_time_greeting():
    """Get appropriate greeting based on time of day"""
    now = datetime.now()
    hour = now.hour
    
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 21:
        return "Good evening"
    else:
        return "Good night"

def startup_greeting():
    """Give a personalized welcome message on startup"""
    global startup_greeting_done
    
    if startup_greeting_done:
        return
        
    username = get_username()
    time_greeting = get_time_greeting()
    now = datetime.now()
    
    # Wait a few seconds after startup for system to settle
    time.sleep(3)
    
    # Personalized greeting
    greeting_message = f"{time_greeting}, {username}! I'm Myra, your AI assistant. I'm here and ready to help you today."
    
    speak(greeting_message)
    time.sleep(1)
    speak("Is there anything you need help with right now?")
    
    # Listen for initial response for 10 seconds
    initial_response = listen_for_initial_response()
    
    if initial_response:
        if any(word in initial_response.lower() for word in ["no", "nothing", "not right now", "later"]):
            speak("Alright! I'll be sleeping quietly in the background. Just say 'Hello Myra' whenever you need me!")
        else:
            # User wants something immediately
            global listening_active
            listening_active = True
            speak("Great! What can I do for you?")
            process_startup_request(initial_response)
    else:
        speak("No problem! I'll be sleeping quietly in the background. Just say 'Hello Myra' whenever you need me!")
    
    startup_greeting_done = True

def listen_for_initial_response():
    """Listen for user's initial response after greeting"""
    try:
        with sr.Microphone() as source:
            print("👂 Listening for initial response...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
        
        command = recognizer.recognize_google(audio)
        print(f"User initial response: {command}")
        return command
    except (sr.UnknownValueError, sr.WaitTimeoutError, sr.RequestError):
        return None

def process_startup_request(command):
    """Process the user's startup request"""
    global listening_active
    
    # Check for system control commands
    system_response = control_system(command)
    if system_response:
        speak(system_response)
        listening_active = False
        return
    
    # Get AI response for general questions
    answer = ask_ollama(command)
    if answer:
        speak(answer)
    
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

def speak(text):
    """Text to speech function"""
    print("Myra:", text)
    engine.say(text)
    engine.runAndWait()

def listen_for_wake_word():
    """Continuously listen for wake word in the background"""
    global listening_active, startup_greeting_done
    
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    
    # Do startup greeting first
    if not startup_greeting_done:
        startup_greeting()
    
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
                
                # Check if any wake word is detected
                if any(wake_word in command for wake_word in WAKE_WORDS):
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
            recognizer.adjust_for_ambient_noise(source, duration=1)
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
        
        increase_words = [
            "increase", "up", "higher", "brighter", "bright", "more", 
            "raise", "turn up", "boost", "enhance", "amplify", "max", "maximum"
        ]
        
        decrease_words = [
            "decrease", "down", "lower", "darker", "dark", "less", "dim", 
            "reduce", "turn down", "minimize", "min", "minimum", "lessen"
        ]
        
        if any(word in action_lower for word in increase_words):
            subprocess.run(["powershell", "-Command", 
                          "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, 100)"], 
                          check=True, capture_output=True)
            return "Brightness increased to maximum."
        
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
        
        try:
            if any(word in command_lower for word in mute_words):
                subprocess.run(["powershell", "-Command", 
                              "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{VOLUME_MUTE}')"], 
                              check=True)
                return "Audio muted."
            elif any(word in command_lower for word in volume_up_words):
                for _ in range(5):
                    subprocess.run(["powershell", "-Command", 
                                  "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{VOLUME_UP}')"], 
                                  check=True)
                return "Volume increased."
            elif any(word in command_lower for word in volume_down_words):
                for _ in range(5):
                    subprocess.run(["powershell", "-Command", 
                                  "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{VOLUME_DOWN}')"], 
                                  check=True)
                return "Volume decreased."
            else:
                return "Would you like me to turn the volume up, down, or mute it?"
        except:
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
        
        # Get AI response for general questions
        answer = ask_ollama(query)
        if answer:
            speak(answer)

def main():
    """Main function"""
    if not MODEL_NAME:
        print("❌ No AI models available. Please install one first.")
        return
    
    print("🤖 Myra Voice Assistant - Startup Mode")
    print("🌅 Starting up with personalized greeting...")
    print("🛑 To stop completely, use Ctrl+C")
    
    try:
        # Start wake word detection with startup greeting
        listen_for_wake_word()
    except KeyboardInterrupt:
        print("\n👋 Myra is shutting down. Goodbye!")

if __name__ == "__main__":
    main()
