#!/usr/bin/env python3
"""
Build script to create Myra Voice Assistant installer .exe
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

def create_build_directory():
    """Create build directory structure"""
    build_dir = "myra_build"
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    
    os.makedirs(build_dir, exist_ok=True)
    
    # Copy necessary files
    files_to_copy = [
        "myra_installer.py",
        "myra_hybrid.py",
        "download_vosk_model.py"
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(build_dir, file))
            print(f"✅ Copied {file}")
        else:
            print(f"⚠️  {file} not found, creating placeholder")
    
    return build_dir

def create_icon():
    """Create a simple icon file"""
    # This is a placeholder - in a real scenario, you'd have a proper .ico file
    icon_content = """
# This would be a proper .ico file in a real implementation
# For now, we'll create a placeholder
"""
    return "myra_icon.ico"

def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['myra_installer.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('myra_hybrid.py', '.'),
        ('download_vosk_model.py', '.'),
    ],
    hiddenimports=[
        'speech_recognition',
        'pyttsx3',
        'requests',
        'tkinter',
        'threading',
        'zipfile',
        'json',
        'win32com.client'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MyraVoiceAssistant_Installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # version='version_info.txt',
    # icon='myra_icon.ico'
)
'''
    
    with open("myra_build/myra_installer.spec", "w") as f:
        f.write(spec_content)
    
    print("✅ Created spec file")

def create_version_info():
    """Create version info file"""
    version_info = '''# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1,0,0,0),
    prodvers=(1,0,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x4,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Myra AI'),
        StringStruct(u'FileDescription', u'Myra Voice Assistant Installer'),
        StringStruct(u'FileVersion', u'1.0.0'),
        StringStruct(u'InternalName', u'MyraInstaller'),
        StringStruct(u'LegalCopyright', u'Copyright 2025 Myra AI'),
        StringStruct(u'OriginalFilename', u'MyraVoiceAssistant_Installer.exe'),
        StringStruct(u'ProductName', u'Myra Voice Assistant'),
        StringStruct(u'ProductVersion', u'1.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    with open("myra_build/version_info.txt", "w", encoding="utf-8") as f:
        f.write(version_info)
    
    print("✅ Created version info")

def install_build_dependencies():
    """Install dependencies needed for building"""
    dependencies = [
        "pyinstaller",
        "pywin32",
    ]
    
    for dep in dependencies:
        print(f"Installing {dep}...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
            print(f"✅ {dep} installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
            return False
    return True

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building Myra Voice Assistant installer...")
    
    build_dir = "myra_build"
    os.chdir(build_dir)
    
    try:
        # Build with PyInstaller
        cmd = [
            "pyinstaller",
            "--clean",
            "myra_installer.spec"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build completed successfully!")
            
            # Copy the executable to the parent directory
            exe_source = os.path.join("dist", "MyraVoiceAssistant_Installer.exe")
            exe_dest = os.path.join("..", "MyraVoiceAssistant_Installer.exe")
            
            if os.path.exists(exe_source):
                shutil.copy2(exe_source, exe_dest)
                print(f"✅ Installer created: MyraVoiceAssistant_Installer.exe")
                print(f"📁 Size: {os.path.getsize(exe_dest) / (1024*1024):.1f} MB")
            else:
                print("❌ Executable not found in dist directory")
                
        else:
            print(f"❌ Build failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Build error: {e}")
    
    os.chdir("..")

def create_readme():
    """Create README for the installer"""
    readme_content = """# Myra Voice Assistant Installer

## 🤖 About Myra
Myra is an advanced AI-powered voice assistant that combines the best of online and offline capabilities.

## 🚀 Features
- **Hybrid Speech Recognition**: Online (Google) + Offline (Vosk)
- **Local AI**: Powered by Ollama for privacy
- **Memory**: Remembers your conversations and preferences
- **System Control**: Brightness, volume, power management
- **File Operations**: Intelligent file and folder search
- **Cross-Session Continuity**: Maintains context across sessions

## 💾 Installation
1. Download `MyraVoiceAssistant_Installer.exe`
2. Run as administrator (recommended)
3. Follow the installation wizard
4. Choose your preferred options:
   - ✅ Desktop shortcut
   - ✅ Offline speech recognition
   - ✅ Ollama AI (recommended)

## 🎯 System Requirements
- Windows 10/11
- Python 3.7+ (will be installed if needed)
- 2GB free disk space
- Microphone for voice input
- Internet connection for initial setup

## 🔧 Manual Installation
If the installer fails, you can manually:
1. Install Python 3.7+
2. Install required packages: `pip install speech_recognition pyttsx3 requests psutil pyautogui vosk pyaudio`
3. Download and run the Myra scripts

## 🎤 Usage
After installation:
1. Run "Myra Voice Assistant" from desktop or Start menu
2. Say "Hello Myra" to wake her up
3. Start giving commands!

## 🗣️ Example Commands
- "Hello Myra" - Wake up
- "My name is John" - Introduction
- "Open calculator" - Launch apps
- "Increase brightness" - System control
- "Remember I like pizza" - Memory
- "What do you know about me?" - Recall
- "Open squid game" - Smart file search

## 🛡️ Privacy
- All AI processing happens locally (Ollama)
- Speech recognition can work offline
- No data sent to external servers (except Google Speech when online)
- Memory stored locally in JSON format

## 🆘 Support
If you encounter issues:
1. Check if Python is properly installed
2. Ensure microphone permissions are granted
3. Try running as administrator
4. Check antivirus software isn't blocking Myra

Enjoy your new AI assistant! 🎉
"""
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ Created README.md")

def main():
    """Main build process"""
    print("🚀 Building Myra Voice Assistant Installer")
    print("=" * 50)
    
    # Step 1: Install build dependencies
    if not install_build_dependencies():
        return
    
    # Step 2: Create build directory
    build_dir = create_build_directory()
    
    # Step 3: Create necessary files
    create_spec_file()
    create_version_info()
    create_readme()
    
    # Step 4: Build executable
    build_executable()
    
    print("\n" + "=" * 50)
    print("🎉 Build process completed!")
    print("\nNext steps:")
    print("1. Test the installer: MyraVoiceAssistant_Installer.exe")
    print("2. Share the installer with others")
    print("3. Users just need to run the .exe - no Python knowledge required!")

if __name__ == "__main__":
    main()
