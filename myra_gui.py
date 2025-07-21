import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
import threading
import time
import speech_recognition as sr
import pyttsx3
import requests
import json
import os
import subprocess
import webbrowser
import psutil
import pyautogui
from pathlib import Path
import re
import shutil
from datetime import datetime
import getpass

# Set the appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

class MyraGUI:
    def __init__(self):
        # Initialize main window
        self.root = ctk.CTk()
        self.root.title("🤖 Myra Voice Assistant")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        
        # Initialize voice components
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.setup_voice()
        
        # State variables
        self.is_listening = False
        self.is_active = False
        self.is_sleeping = True
        
        # Wake words with better pattern matching
        self.wake_words = ["hello myra", "hey myra", "hi myra", "myra", "okay myra"]
        # Configure recognizer for better accuracy
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        
        # Setup Ollama
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = self.select_model()
        
        # Create GUI elements
        self.setup_gui()
        
        # Start background listening thread
        self.listening_thread = threading.Thread(target=self.listen_loop, daemon=True)
        self.listening_thread.start()
        
        # Original update interval was too high; reduce to once per second
        self.root.after(1000, self.update_status)
        
    def setup_voice(self):
        """Configure voice to be female"""
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        else:
            if len(voices) > 1:
                self.engine.setProperty('voice', voices[1].id)
        
        self.engine.setProperty('rate', 180)
        self.engine.setProperty('volume', 0.9)
    
    def select_model(self):
        """Select the best available Ollama model"""
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json()
                if models.get('models'):
                    preferred = ['llama3.2:1b', 'llama3.2:3b', 'mistral:latest']
                    for pref in preferred:
                        for model in models['models']:
                            if model['name'] == pref:
                                return pref
                    return models['models'][0]['name']
        except:
            pass
        return None
    
    def setup_gui(self):
        """Create the GUI elements"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="🤖 Myra",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.title_label.pack(pady=(20, 10))
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.main_frame,
            text="Your AI Voice Assistant",
            font=ctk.CTkFont(size=14)
        )
        self.subtitle_label.pack(pady=(0, 20))
        
        # Status indicator (circle)
        self.status_frame = ctk.CTkFrame(self.main_frame, height=150)
        self.status_frame.pack(fill="x", pady=10)
        
        # Create canvas for status circle
        self.canvas = tk.Canvas(
            self.status_frame,
            width=120,
            height=120,
            bg='#212121',
            highlightthickness=0
        )
        self.canvas.pack(pady=20)
        
        # Status text
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="😴 Sleeping",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.status_label.pack(pady=10)
        
        # Activity log
        self.activity_frame = ctk.CTkFrame(self.main_frame)
        self.activity_frame.pack(fill="both", expand=True, pady=10)
        
        self.activity_label = ctk.CTkLabel(
            self.activity_frame,
            text="Activity Log",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.activity_label.pack(pady=(10, 5))
        
        # Scrollable text widget for activity
        self.activity_text = ctk.CTkTextbox(
            self.activity_frame,
            height=150,
            font=ctk.CTkFont(size=12)
        )
        self.activity_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Control buttons
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(fill="x", pady=10)
        
        # Wake/Sleep button
        self.wake_button = ctk.CTkButton(
            self.button_frame,
            text="💤 Wake Up",
            command=self.toggle_wake_sleep,
            font=ctk.CTkFont(size=14),
            height=40
        )
        self.wake_button.pack(side="left", padx=(10, 5), pady=10, fill="x", expand=True)
        
        # Settings button
        self.settings_button = ctk.CTkButton(
            self.button_frame,
            text="⚙️ Settings",
            command=self.open_settings,
            font=ctk.CTkFont(size=14),
            height=40
        )
        self.settings_button.pack(side="right", padx=(5, 10), pady=10, fill="x", expand=True)
        
        # System info frame
        self.info_frame = ctk.CTkFrame(self.main_frame)
        self.info_frame.pack(fill="x", pady=(10, 0))
        
        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text=f"👋 Hello, {getpass.getuser()}!",
            font=ctk.CTkFont(size=14)
        )
        self.info_label.pack(pady=10)
        
        # Initial activity log entry
        self.log_activity("🚀 Myra initialized and ready!")
        self.log_activity("💤 Sleeping - say 'Hello Myra' to wake me up")
    
    def draw_status_circle(self, color, pulse=False):
        """Draw the status indicator circle"""
        self.canvas.delete("all")
        
        # Outer ring
        ring_color = color if not pulse else "#FF6B6B"
        self.canvas.create_oval(10, 10, 110, 110, outline=ring_color, width=3, fill="")
        
        # Inner circle
        inner_color = color
        if pulse:
            # Create pulsing effect
            radius = 35 + (5 * (time.time() % 1))
            self.canvas.create_oval(60-radius, 60-radius, 60+radius, 60+radius, 
                                  fill=inner_color, outline="")
        else:
            self.canvas.create_oval(25, 25, 95, 95, fill=inner_color, outline="")
        
        # Center dot
        self.canvas.create_oval(55, 55, 65, 65, fill="white", outline="")
    
    def log_activity(self, message):
        """Add a message to the activity log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        # Add to textbox
        self.activity_text.insert("end", log_message)
        self.activity_text.see("end")  # Scroll to bottom
    
    def speak(self, text):
        """Text to speech with GUI updates"""
        self.log_activity(f"🗣️ Myra: {text}")
        
        def speak_thread():
            self.engine.say(text)
            self.engine.runAndWait()
        
        threading.Thread(target=speak_thread, daemon=True).start()
    
    def check_wake_word(self, command):
        """Check if wake word is detected with fuzzy matching"""
        command_lower = command.lower()
        
        # Direct matches
        if any(wake_word in command_lower for wake_word in self.wake_words):
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
                self.log_activity(f"🔧 Corrected '{misrecognition}' to '{correct}'")
                return True
                
        return False

    def listen_loop(self):
        """Background listening loop for wake words"""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        # Improved listening loop with reduced blocking
        while True:
            if not self.is_sleeping:
                time.sleep(0.1)  # Sleep less frequently when awake
                continue
            
            try:
                with sr.Microphone() as source:
                    # Optimize ambient noise adjustment
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                
                try:
                    command = self.recognizer.recognize_google(audio).lower()
                    self.log_activity(f"👂 Heard: {command}")
                    
                    # Check for wake words with fuzzy matching
                    if self.check_wake_word(command):
                        self.log_activity("🚀 Wake word detected!")
                        self.wake_up()
                        
                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    self.log_activity("❌ Speech service unavailable")
                    time.sleep(5)
                    
            except sr.WaitTimeoutError:
                pass
            except Exception as e:
                self.log_activity(f"❌ Listening error: {str(e)}")
                time.sleep(1)
    
    def wake_up(self):
        """Wake up Myra"""
        self.is_sleeping = False
        self.is_active = True
        self.status_label.configure(text="👁️ Awake & Listening")
        self.wake_button.configure(text="😴 Go to Sleep")
        self.log_activity("👁️ Myra is now awake!")
        
        username = getpass.getuser()
        time_greeting = self.get_time_greeting()
        
        self.speak(f"{time_greeting}, {username}! I'm awake. How can I help you?")
        
        # Start active listening
        threading.Thread(target=self.active_listen_loop, daemon=True).start()
    
    def go_to_sleep(self):
        """Put Myra to sleep"""
        self.is_sleeping = True
        self.is_active = False
        self.status_label.configure(text="😴 Sleeping")
        self.wake_button.configure(text="💤 Wake Up")
        self.log_activity("😴 Myra is going to sleep")
        self.speak("Going to sleep. Say 'Hello Myra' to wake me up!")
    
    def toggle_wake_sleep(self):
        """Toggle between wake and sleep states"""
        if self.is_sleeping:
            self.wake_up()
        else:
            self.go_to_sleep()
    
    def active_listen_loop(self):
        """Active listening loop when awake"""
        inactive_count = 0
        
        while self.is_active and not self.is_sleeping:
            try:
                with sr.Microphone() as source:
                    self.log_activity("👂 Listening for command...")
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=7)
                
                command = self.recognizer.recognize_google(audio)
                self.log_activity(f"🎤 You: {command}")
                
                # Process command
                response = self.process_command(command)
                if response:
                    self.speak(response)
                
                inactive_count = 0
                
            except sr.UnknownValueError:
                self.log_activity("❓ Didn't catch that")
                inactive_count += 1
            except sr.WaitTimeoutError:
                inactive_count += 1
            except sr.RequestError:
                self.log_activity("❌ Speech service error")
                break
            
            # Auto-sleep after inactivity
            if inactive_count >= 3:
                self.log_activity("💤 Auto-sleeping due to inactivity")
                self.go_to_sleep()
                break
    
    def process_command(self, command):
        """Process voice commands"""
        command_lower = command.lower()
        
        # Sleep commands
        if any(x in command_lower for x in ["go to sleep", "sleep now", "goodbye myra"]):
            self.go_to_sleep()
            return None
        
        # System info
        if "system info" in command_lower or "pc info" in command_lower:
            try:
                cpu_usage = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                return f"CPU usage: {cpu_usage}%, Memory usage: {memory.percent}%"
            except:
                return "Sorry, couldn't get system information"
        
        # Time
        if "time" in command_lower:
            now = datetime.now()
            return f"The current time is {now.strftime('%I:%M %p')}"
        
        # Date
        if "date" in command_lower:
            now = datetime.now()
            return f"Today is {now.strftime('%A, %B %d, %Y')}"
        
        # Apps
        if "open calculator" in command_lower:
            os.system("calc")
            return "Calculator opened"
        
        if "open notepad" in command_lower:
            os.system("notepad")
            return "Notepad opened"
        
        # Web search
        if "search" in command_lower or "google" in command_lower:
            query = command_lower.replace("search ", "").replace("google ", "")
            if query:
                webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
                return f"Searching for {query}"
        
        # AI response via Ollama
        if self.model_name:
            return self.ask_ollama(command)
        
        return "I'm not sure how to help with that"
    
    def ask_ollama(self, prompt):
        """Get AI response from Ollama"""
        if not self.model_name:
            return "Sorry, no AI model is available"
        
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(self.ollama_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'No response available')
            
        except Exception as e:
            return "Sorry, I couldn't process that request"
        
        return "Sorry, something went wrong"
    
    def get_time_greeting(self):
        """Get appropriate greeting based on time"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "Good morning"
        elif 12 <= hour < 17:
            return "Good afternoon"
        elif 17 <= hour < 21:
            return "Good evening"
        else:
            return "Good night"
    
    def open_settings(self):
        """Open settings window"""
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("Myra Settings")
        settings_window.geometry("300x400")
        
        # Settings content
        settings_label = ctk.CTkLabel(
            settings_window,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        settings_label.pack(pady=20)
        
        # Voice speed
        speed_label = ctk.CTkLabel(settings_window, text="Voice Speed:")
        speed_label.pack(pady=(20, 5))
        
        speed_slider = ctk.CTkSlider(settings_window, from_=100, to=300, number_of_steps=20)
        speed_slider.set(180)
        speed_slider.pack(pady=5)
        
        # Volume
        volume_label = ctk.CTkLabel(settings_window, text="Voice Volume:")
        volume_label.pack(pady=(20, 5))
        
        volume_slider = ctk.CTkSlider(settings_window, from_=0.1, to=1.0, number_of_steps=9)
        volume_slider.set(0.9)
        volume_slider.pack(pady=5)
        
        # Apply button
        def apply_settings():
            self.engine.setProperty('rate', int(speed_slider.get()))
            self.engine.setProperty('volume', volume_slider.get())
            self.log_activity("⚙️ Settings updated")
            settings_window.destroy()
        
        apply_button = ctk.CTkButton(
            settings_window,
            text="Apply Settings",
            command=apply_settings
        )
        apply_button.pack(pady=20)
    
    def update_status(self):
        """Update status indicators"""
        if self.is_sleeping:
            self.draw_status_circle("#4A90E2")  # Blue for sleeping
        elif self.is_active:
            self.draw_status_circle("#50C878", pulse=True)  # Green pulsing for active
        else:
            self.draw_status_circle("#FFA500")  # Orange for idle
        
        # Schedule next update
        self.root.after(100, self.update_status)
    
    def run(self):
        """Start the GUI"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.log_activity("👋 Shutting down Myra...")

def main():
    """Main function"""
    print("🚀 Starting Myra GUI...")
    app = MyraGUI()
    app.run()

if __name__ == "__main__":
    main()
