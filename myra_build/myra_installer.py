#!/usr/bin/env python3
"""
🤖 Myra Voice Assistant - Professional Installer
Complete setup script that installs Myra on any Windows PC
"""
import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import requests
import zipfile
import shutil
from pathlib import Path
import json

class MyraInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Myra Voice Assistant - Installer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Set icon (if available)
        try:
            self.root.iconbitmap("myra_icon.ico")
        except:
            pass
        
        # Installation directory
        self.install_dir = os.path.join(os.path.expanduser("~"), "MyraAI")
        self.progress_var = tk.StringVar()
        self.progress_var.set("Ready to install Myra Voice Assistant")
        
        self.create_ui()
        
    def create_ui(self):
        """Create the installer UI"""
        # Header
        header_frame = tk.Frame(self.root, bg="#2C3E50", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🤖 Myra Voice Assistant", 
                              font=("Arial", 18, "bold"), fg="white", bg="#2C3E50")
        title_label.pack(pady=20)
        
        # Main content
        main_frame = tk.Frame(self.root, padx=30, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Welcome message
        welcome_text = """Welcome to Myra Voice Assistant Setup!
        
Myra is an advanced AI-powered voice assistant that can:
• Control your computer (brightness, volume, power)
• Open applications and files intelligently
• Remember your preferences and conversations
• Work both online and offline
• Answer questions using local AI

This installer will set up everything you need to run Myra."""
        
        welcome_label = tk.Label(main_frame, text=welcome_text, justify="left", 
                                font=("Arial", 10), wraplength=500)
        welcome_label.pack(pady=(0, 20))
        
        # Installation directory selection
        dir_frame = tk.Frame(main_frame)
        dir_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(dir_frame, text="Installation Directory:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        dir_select_frame = tk.Frame(dir_frame)
        dir_select_frame.pack(fill="x", pady=(5, 0))
        
        self.dir_entry = tk.Entry(dir_select_frame, font=("Arial", 10))
        self.dir_entry.insert(0, self.install_dir)
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(dir_select_frame, text="Browse", command=self.browse_directory)
        browse_btn.pack(side="right")
        
        # Options
        options_frame = tk.LabelFrame(main_frame, text="Installation Options", padx=10, pady=10)
        options_frame.pack(fill="x", pady=(0, 20))
        
        self.create_desktop_shortcut = tk.BooleanVar(value=True)
        self.install_offline_speech = tk.BooleanVar(value=True)
        self.install_ollama = tk.BooleanVar(value=True)
        
        tk.Checkbutton(options_frame, text="Create desktop shortcut", 
                      variable=self.create_desktop_shortcut).pack(anchor="w")
        tk.Checkbutton(options_frame, text="Install offline speech recognition", 
                      variable=self.install_offline_speech).pack(anchor="w")
        tk.Checkbutton(options_frame, text="Install Ollama AI (recommended)", 
                      variable=self.install_ollama).pack(anchor="w")
        
        # Progress
        progress_frame = tk.Frame(main_frame)
        progress_frame.pack(fill="x", pady=(0, 20))
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill="x", pady=(0, 5))
        
        self.progress_label = tk.Label(progress_frame, textvariable=self.progress_var, 
                                      font=("Arial", 9))
        self.progress_label.pack()
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        self.install_btn = tk.Button(button_frame, text="Install Myra", 
                                    font=("Arial", 12, "bold"), bg="#3498DB", fg="white",
                                    command=self.start_installation, padx=20, pady=10)
        self.install_btn.pack(side="right", padx=(10, 0))
        
        cancel_btn = tk.Button(button_frame, text="Cancel", 
                              command=self.root.quit, padx=20, pady=10)
        cancel_btn.pack(side="right")
    
    def browse_directory(self):
        """Browse for installation directory"""
        directory = filedialog.askdirectory(initialdir=self.install_dir)
        if directory:
            self.install_dir = directory
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
    
    def update_progress(self, message):
        """Update progress message"""
        self.progress_var.set(message)
        self.root.update()
    
    def start_installation(self):
        """Start the installation process"""
        self.install_dir = self.dir_entry.get()
        self.install_btn.config(state="disabled")
        self.progress_bar.start()
        
        # Run installation in a separate thread
        install_thread = threading.Thread(target=self.install_myra)
        install_thread.daemon = True
        install_thread.start()
    
    def install_python_packages(self):
        """Install required Python packages"""
        packages = [
            "speech_recognition", "pyttsx3", "requests", "psutil", "pyautogui"
        ]
        
        if self.install_offline_speech.get():
            packages.extend(["vosk", "pyaudio"])
        
        for package in packages:
            self.update_progress(f"Installing {package}...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Installation Error", 
                                   f"Failed to install {package}: {e}")
                return False
        return True
    
    def download_vosk_model(self):
        """Download Vosk speech recognition model"""
        if not self.install_offline_speech.get():
            return True
            
        model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
        model_zip = os.path.join(self.install_dir, "vosk-model.zip")
        model_dir = os.path.join(self.install_dir, "vosk-model")
        
        if os.path.exists(model_dir):
            return True  # Already exists
            
        self.update_progress("Downloading offline speech model...")
        
        try:
            response = requests.get(model_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(model_zip, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        self.update_progress(f"Downloading model... {percent:.1f}%")
            
            self.update_progress("Extracting speech model...")
            with zipfile.ZipFile(model_zip, 'r') as zip_ref:
                zip_ref.extractall(self.install_dir)
            
            # Rename extracted directory
            for item in os.listdir(self.install_dir):
                if item.startswith('vosk-model') and os.path.isdir(os.path.join(self.install_dir, item)):
                    if item != 'vosk-model':
                        os.rename(os.path.join(self.install_dir, item), model_dir)
                    break
            
            os.remove(model_zip)
            return True
            
        except Exception as e:
            messagebox.showerror("Download Error", f"Failed to download speech model: {e}")
            return False
    
    def install_ollama(self):
        """Install Ollama AI"""
        if not self.install_ollama.get():
            return True
            
        self.update_progress("Downloading Ollama AI...")
        
        try:
            # Download Ollama installer
            ollama_url = "https://ollama.ai/download/windows"
            ollama_installer = os.path.join(self.install_dir, "ollama-installer.exe")
            
            response = requests.get(ollama_url, stream=True)
            response.raise_for_status()
            
            with open(ollama_installer, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.update_progress("Installing Ollama AI...")
            subprocess.run([ollama_installer, "/S"], check=True)  # Silent install
            
            os.remove(ollama_installer)
            
            # Download LLaMA model
            self.update_progress("Setting up AI model...")
            subprocess.run(["ollama", "pull", "llama3.2:1b"], check=True)
            
            return True
            
        except Exception as e:
            messagebox.showwarning("Ollama Installation", 
                                 f"Ollama installation failed: {e}\\nYou can install it manually later.")
            return True  # Continue installation even if Ollama fails
    
    def copy_myra_files(self):
        """Copy Myra application files"""
        self.update_progress("Installing Myra application...")
        
        # Create installation directory
        os.makedirs(self.install_dir, exist_ok=True)
        
        # Copy the hybrid Myra file (assuming it's in the same directory)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        myra_source = os.path.join(current_dir, "myra_hybrid.py")
        myra_dest = os.path.join(self.install_dir, "myra.py")
        
        if os.path.exists(myra_source):
            shutil.copy2(myra_source, myra_dest)
        else:
            # Create a basic version if source not found
            self.create_myra_application()
        
        # Create batch file for easy execution
        batch_content = f'''@echo off
cd /d "{self.install_dir}"
python myra.py
pause'''
        
        with open(os.path.join(self.install_dir, "Start Myra.bat"), "w") as f:
            f.write(batch_content)
        
        return True
    
    def create_myra_application(self):
        """Create Myra application file if source not available"""
        myra_content = '''#!/usr/bin/env python3
"""
🤖 Myra Voice Assistant - Installed Version
"""
print("Myra Voice Assistant is starting...")
print("This is a basic version. Please update with the full Myra code.")
'''
        
        with open(os.path.join(self.install_dir, "myra.py"), "w") as f:
            f.write(myra_content)
    
    def create_desktop_shortcut(self):
        """Create desktop shortcut"""
        if not self.create_desktop_shortcut.get():
            return True
            
        self.update_progress("Creating desktop shortcut...")
        
        try:
            import win32com.client
            
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut_path = os.path.join(desktop, "Myra Voice Assistant.lnk")
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = os.path.join(self.install_dir, "Start Myra.bat")
            shortcut.WorkingDirectory = self.install_dir
            shortcut.IconLocation = os.path.join(self.install_dir, "myra_icon.ico")
            shortcut.save()
            
            return True
            
        except Exception as e:
            messagebox.showwarning("Shortcut Creation", 
                                 f"Could not create desktop shortcut: {e}")
            return True  # Continue even if shortcut creation fails
    
    def install_myra(self):
        """Main installation process"""
        try:
            # Step 1: Install Python packages
            if not self.install_python_packages():
                return
            
            # Step 2: Copy Myra files
            if not self.copy_myra_files():
                return
            
            # Step 3: Download Vosk model
            if not self.download_vosk_model():
                return
            
            # Step 4: Install Ollama
            if not self.install_ollama():
                return
            
            # Step 5: Create desktop shortcut
            if not self.create_desktop_shortcut():
                return
            
            # Finish installation
            self.progress_bar.stop()
            self.update_progress("Installation completed successfully!")
            
            messagebox.showinfo("Installation Complete", 
                              f"Myra Voice Assistant has been successfully installed!\\n\\n"
                              f"Installation Directory: {self.install_dir}\\n\\n"
                              f"You can now run Myra from the desktop shortcut or by running "
                              f"'Start Myra.bat' in the installation directory.")
            
            self.root.quit()
            
        except Exception as e:
            self.progress_bar.stop()
            messagebox.showerror("Installation Failed", f"Installation failed: {e}")
            self.install_btn.config(state="normal")
    
    def run(self):
        """Run the installer"""
        self.root.mainloop()

if __name__ == "__main__":
    installer = MyraInstaller()
    installer.run()
