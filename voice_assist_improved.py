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
    # If no female voice found, try to use the second voice (often female on Windows)
    if len(voices) > 1:
        engine.setProperty('voice', voices[1].id)
        print(f"🎤 Using voice: {voices[1].name}")
    else:
        print(f"🎤 Using default voice: {voices[0].name if voices else 'Unknown'}")

# Set speech rate and volume
engine.setProperty('rate', 180)  # Slightly slower for clarity
engine.setProperty('volume', 0.9)  # 90% volume

OLLAMA_URL = "http://localhost:11434/api/generate"

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
    
    # Priority order: prefer llama models, then anything else
    preferred_models = [
        'llama3.2:3b', 'llama3.2:1b', 'llama3.1:8b', 'llama3.1:7b',
        'mistral:7b', 'mistral:latest', 'gemma:7b', 'codellama:7b'
    ]
    
    for preferred in preferred_models:
        if preferred in models:
            print(f"✅ Using model: {preferred}")
            return preferred
    
    # If no preferred model, use the first available
    selected = models[0]
    print(f"✅ Using model: {selected}")
    return selected

MODEL_NAME = select_model()

# === Speak ===
def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

# === Listen ===
def listen():
    with sr.Microphone() as source:
        print("Listening...")
        try:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            print("Listening timeout...")
            return ""

    try:
        command = recognizer.recognize_google(audio)
        print("You:", command)
        return command
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError as e:
        speak("Sorry, speech service is down.")
        print(f"Speech service error: {e}")
        return ""

# === System Control Functions ===
def adjust_brightness(action):
    """Adjust screen brightness with intelligent word recognition"""
    try:
        action_lower = action.lower()
        
        # Words that indicate INCREASE
        increase_words = [
            "increase", "up", "higher", "brighter", "bright", "more", 
            "raise", "turn up", "boost", "enhance", "amplify", "max", "maximum"
        ]
        
        # Words that indicate DECREASE  
        decrease_words = [
            "decrease", "down", "lower", "darker", "dark", "less", "dim", 
            "reduce", "turn down", "minimize", "min", "minimum", "lessen"
        ]
        
        # Check if any increase words are present
        if any(word in action_lower for word in increase_words):
            subprocess.run(["powershell", "-Command", 
                          "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, 100)"], 
                          check=True, capture_output=True)
            return "Brightness increased to maximum."
        
        # Check if any decrease words are present
        elif any(word in action_lower for word in decrease_words):
            subprocess.run(["powershell", "-Command", 
                          "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, 30)"], 
                          check=True, capture_output=True)
            return "Brightness decreased to 30 percent."
        
        # If brightness is mentioned but no clear direction, try to infer from context
        elif "brightness" in action_lower:
            # If they just say "change brightness" or "adjust brightness", ask for clarification
            if any(word in action_lower for word in ["change", "adjust", "set", "modify"]):
                return "Would you like me to make the screen brighter or darker?"
            else:
                # Default to asking for clarification
                return "Should I make the screen brighter or darker?"
        
        else:
            return "I can make your screen brighter or darker. What would you prefer?"
            
    except Exception as e:
        return "Sorry, I couldn't adjust the brightness. This might require administrator privileges."

def control_system(command):
    """Handle system control commands"""
    command_lower = command.lower()
    
    # Shutdown commands
    if any(x in command_lower for x in ["shutdown", "turn off", "power off"]):
        speak("Shutting down the computer in 10 seconds. Say cancel to stop.")
        time.sleep(3)
        # Give user a chance to cancel
        speak("Shutting down now.")
        try:
            os.system("shutdown /s /t 5")
            return "Computer is shutting down."
        except Exception as e:
            return "Sorry, I couldn't shut down the computer."
    
    # Restart commands
    elif any(x in command_lower for x in ["restart", "reboot"]):
        speak("Restarting the computer in 10 seconds. Say cancel to stop.")
        time.sleep(3)
        speak("Restarting now.")
        try:
            os.system("shutdown /r /t 5")
            return "Computer is restarting."
        except Exception as e:
            return "Sorry, I couldn't restart the computer."
    
    # Lock screen commands
    elif any(x in command_lower for x in ["lock", "lock screen", "lock computer"]):
        try:
            os.system("rundll32.exe user32.dll, LockWorkStation")
            return "Screen locked."
        except Exception as e:
            return "Sorry, I couldn't lock the screen."
    
    # Sleep/hibernate commands
    elif any(x in command_lower for x in ["sleep", "hibernate"]):
        try:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "Computer is going to sleep."
        except Exception as e:
            return "Sorry, I couldn't put the computer to sleep."
    
    # Brightness controls
    elif any(x in command_lower for x in ["brightness", "screen brightness"]):
        return adjust_brightness(command_lower)
    
    # Volume controls (enhanced with dynamic word recognition)
    elif "volume" in command_lower or "sound" in command_lower or "audio" in command_lower:
        # Volume increase words
        volume_up_words = ["up", "increase", "higher", "raise", "boost", "more", "louder", "turn up"]
        # Volume decrease words  
        volume_down_words = ["down", "decrease", "lower", "reduce", "less", "quieter", "turn down", "softer"]
        # Mute words
        mute_words = ["mute", "silence", "quiet", "off", "shut up"]
        
        try:
            if any(word in command_lower for word in mute_words):
                subprocess.run(["powershell", "-Command", 
                              "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{VOLUME_MUTE}')"], 
                              check=True)
                return "Audio muted."
            elif any(word in command_lower for word in volume_up_words):
                for _ in range(5):  # Increase volume 5 times
                    subprocess.run(["powershell", "-Command", 
                                  "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{VOLUME_UP}')"], 
                                  check=True)
                return "Volume increased."
            elif any(word in command_lower for word in volume_down_words):
                for _ in range(5):  # Decrease volume 5 times
                    subprocess.run(["powershell", "-Command", 
                                  "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{VOLUME_DOWN}')"], 
                                  check=True)
                return "Volume decreased."
            else:
                return "Would you like me to turn the volume up, down, or mute it?"
        except:
            return "Sorry, I couldn't adjust the volume."
    
    # Open applications dynamically
    elif "open" in command_lower or "launch" in command_lower or "run" in command_lower:
        app_name = command_lower.replace("open ", "").replace("launch ", "").replace("run ", "")
        try:
            if app_name:
                path = shutil.which(app_name)
                if path:
                    os.startfile(path)
                    return f"{app_name.title()} opened."
                else:
                    webbrowser.open(f"https://www.google.com/search?q={app_name}")
                    return f"I couldn't find {app_name.title()}. Opened search in your browser."
            else:
                return "Please specify an application or service to open."
        except Exception as e:
            return f"Sorry, I couldn't open {app_name.title()}. {str(e)}"
    
    # Closing applications
    elif "close" in command_lower or "shut down" in command_lower:
        app_name = command_lower.replace("close ", "").replace("shut down ", "")
        try:
            if app_name:
                for proc in psutil.process_iter(['name']):
                    if re.search(app_name, proc.info['name'], re.IGNORECASE):
                        proc.kill()
                        return f"Closed {proc.info['name']}."
                return f"No open {app_name.title()} application found to close."
            else:
                return "Please specify an application to close."
        except Exception as e:
            return f"Sorry, I couldn't close {app_name.title()}. {str(e)}"

    # Playing music and videos
    elif "play" in command_lower:
        media_path = command_lower.replace("play ", "")
        try:
            media_files = list(Path('.').rglob(f"**/{media_path}*.mp3")) + list(Path('.').rglob(f"**/{media_path}*.mp4"))
            if media_files:
                os.startfile(media_files[0])
                return f"Playing {media_files[0].name}."
            else:
                return f"No media file found for {media_path}."
        except Exception as e:
            return f"Sorry, I couldn't play {media_path}. {str(e)}"

    # Advanced App Management
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
    
    # Playing music from YouTube or local files
    elif "play music" in command_lower or "play song" in command_lower:
        song = command_lower.replace("play music ", "").replace("play song ", "").replace("play ", "")
        try:
            if song:
                # Search YouTube for the song
                search_url = f"https://www.youtube.com/results?search_query={song.replace(' ', '+')}"
                webbrowser.open(search_url)
                return f"Opening YouTube to play {song}."
            else:
                # Open default music app
                os.system("start mswindowsstore://pdp/?ProductId=9WZDNCRFJ3PT")  # Windows Media Player
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
    
    # File management
    elif "create file" in command_lower or "new file" in command_lower:
        filename = command_lower.replace("create file ", "").replace("new file ", "")
        try:
            if filename:
                with open(filename, 'w') as f:
                    f.write(f"# File created by Myra on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                return f"Created file {filename}."
            else:
                return "Please specify a filename."
        except:
            return "Sorry, I couldn't create the file."
    
    # Email handling (opens default mail app)
    elif "email" in command_lower or "mail" in command_lower:
        if "open" in command_lower:
            try:
                os.system("start mailto:")
                return "Opening email client."
            except:
                return "Sorry, I couldn't open the email client."
    
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
    
    # Weather (opens weather website)
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
    
    return None  # Return None if no system command was found

# === Call Ollama ===
def ask_ollama(prompt):
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
        print("Assistant: ", end="", flush=True)
        
        for line in response.iter_lines():
            if line:
                data = line.decode('utf-8')
                try:
                    if data.startswith('{') and 'response' in data:
                        json_data = json.loads(data)
                        text = json_data.get('response', '')
                        print(text, end='', flush=True)
                        reply += text
                        
                        # Check if this is the final response
                        if json_data.get('done', False):
                            break
                except json.JSONDecodeError:
                    continue
        
        print()  # New line after response
        return reply.strip()
        
    except requests.exceptions.Timeout:
        return "Sorry, the AI model is taking too long to respond."
    except requests.exceptions.ConnectionError:
        return "Sorry, I can't connect to the AI service. Is Ollama running?"
    except Exception as e:
        return f"Sorry, there was an error: {str(e)}"

# === Main loop ===
def main():
    if not MODEL_NAME:
        print("❌ No AI models available. Please install one first.")
        return
    
    speak("Hello! I am Myra, your AI assistant. Say something!")
    
    while True:
        query = listen()
        if query == "":
            continue
            
        # Check for exit commands
        if any(x in query.lower() for x in ["bye", "stop", "exit", "quit", "goodbye"]):
            speak("Goodbye! It was nice talking to you!")
            break
        
        # Special commands
        if "what's your name" in query.lower() or "who are you" in query.lower():
            speak("I am Myra, your AI voice assistant!")
            continue
        
        if "what can you do" in query.lower():
            speak("I can answer questions, have conversations, control your computer, adjust brightness, volume, open applications, shut down or restart your PC, and much more! What would you like to do?")
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

if __name__ == "__main__":
    print("🚀 Starting Myra Voice Assistant...")
    main()
