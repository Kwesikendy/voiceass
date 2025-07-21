#!/usr/bin/env python3
"""
Download Vosk model for offline speech recognition
"""
import requests
import zipfile
import os
from pathlib import Path

def download_vosk_model():
    model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    model_zip = "vosk-model.zip" 
    model_dir = "vosk-model"
    
    if os.path.exists(model_dir):
        print("✅ Vosk model already exists")
        return model_dir
    
    print("📥 Downloading Vosk model (this may take a moment)...")
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
                    print(f"\r📥 Downloaded {percent:.1f}%", end="", flush=True)
        
        print("\n📦 Extracting model...")
        with zipfile.ZipFile(model_zip, 'r') as zip_ref:
            zip_ref.extractall('.')
        
        # Find the extracted directory
        for item in os.listdir('.'):
            if item.startswith('vosk-model') and os.path.isdir(item):
                os.rename(item, model_dir)
                break
        
        # Clean up
        os.remove(model_zip)
        print(f"✅ Vosk model ready at: {model_dir}")
        return model_dir
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        return None

if __name__ == "__main__":
    download_vosk_model()
