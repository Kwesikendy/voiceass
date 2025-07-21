#!/usr/bin/env python3
"""
🎤 Myra Microphone Detection and Setup
Check available microphones and test audio input
"""
import speech_recognition as sr
import pyaudio
import time

def list_microphones():
    """List all available microphones"""
    print("🎤 Available Microphones:")
    print("=" * 50)
    
    # Get microphone list from speech_recognition
    mic_list = sr.Microphone.list_microphone_names()
    
    if not mic_list:
        print("❌ No microphones found!")
        return []
    
    for i, microphone_name in enumerate(mic_list):
        print(f"{i}: {microphone_name}")
    
    return mic_list

def list_pyaudio_devices():
    """List PyAudio devices for more detailed info"""
    print("\n🔊 PyAudio Audio Devices:")
    print("=" * 50)
    
    try:
        audio = pyaudio.PyAudio()
        
        print(f"Default input device: {audio.get_default_input_device_info()['name']}")
        print(f"Default output device: {audio.get_default_output_device_info()['name']}")
        print()
        
        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            print(f"Device {i}: {info['name']}")
            print(f"  Channels: {info['maxInputChannels']} in, {info['maxOutputChannels']} out")
            print(f"  Sample Rate: {info['defaultSampleRate']} Hz")
            if info['maxInputChannels'] > 0:
                print(f"  ✅ Can be used for input")
            print()
        
        audio.terminate()
        
    except Exception as e:
        print(f"❌ Error accessing PyAudio: {e}")

def test_microphone(mic_index=None):
    """Test a specific microphone"""
    mic_name = mic_index if mic_index is not None else '(default)'
    print(f"\n🧪 Testing Microphone {mic_name}:")
    print("=" * 50)
    
    recognizer = sr.Recognizer()
    
    try:
        if mic_index is not None:
            microphone = sr.Microphone(device_index=mic_index)
        else:
            microphone = sr.Microphone()
        
        with microphone as source:
            print("🔧 Adjusting for ambient noise... Please wait.")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print(f"✅ Energy threshold set to: {recognizer.energy_threshold}")
            
        print("🎤 Say something! Listening for 5 seconds...")
        
        with microphone as source:
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                print("🎵 Audio captured successfully!")
                
                # Try to recognize
                print("🧠 Attempting speech recognition...")
                try:
                    text = recognizer.recognize_google(audio)
                    print(f"✅ Recognized: '{text}'")
                    return True
                except sr.UnknownValueError:
                    print("⚠️ Audio captured but could not understand speech")
                    return True  # Mic works, just didn't understand
                except sr.RequestError as e:
                    print(f"⚠️ Speech recognition service error: {e}")
                    return True  # Mic works, service issue
                    
            except sr.WaitTimeoutError:
                print("⏰ No audio detected in 5 seconds")
                return False
                
    except Exception as e:
        print(f"❌ Error testing microphone: {e}")
        return False

def interactive_mic_setup():
    """Interactive microphone setup for Myra"""
    print("\n🎤 Interactive Microphone Setup for Myra")
    print("=" * 50)
    
    mic_list = list_microphones()
    if not mic_list:
        return None
    
    while True:
        try:
            choice = input(f"\nEnter microphone index (0-{len(mic_list)-1}) or 'test' to test current default: ").strip().lower()
            
            if choice == 'test':
                if test_microphone():
                    print("✅ Default microphone works!")
                    return None
                else:
                    print("❌ Default microphone has issues")
                    continue
            
            elif choice == 'quit' or choice == 'exit':
                return None
                
            else:
                mic_index = int(choice)
                if 0 <= mic_index < len(mic_list):
                    print(f"Testing: {mic_list[mic_index]}")
                    if test_microphone(mic_index):
                        print(f"✅ Microphone {mic_index} works!")
                        return mic_index
                    else:
                        print(f"❌ Microphone {mic_index} has issues")
                else:
                    print("❌ Invalid microphone index")
                    
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            return None

def create_microphone_config(mic_index=None):
    """Create a microphone configuration file for Myra"""
    config = {
        "microphone_index": mic_index,
        "energy_threshold": 300,
        "dynamic_energy_threshold": True,
        "pause_threshold": 0.8,
        "phrase_threshold": 0.3,
        "non_speaking_duration": 0.8
    }
    
    import json
    with open("myra_microphone_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Microphone configuration saved to myra_microphone_config.json")
    if mic_index is not None:
        print(f"   Using microphone index: {mic_index}")
    else:
        print("   Using default microphone")

def main():
    """Main function"""
    print("🎤 Myra Microphone Detection and Setup Tool")
    print("=" * 60)
    
    # List all available microphones
    list_microphones()
    
    # List PyAudio devices for detailed info
    list_pyaudio_devices()
    
    # Interactive setup
    mic_index = interactive_mic_setup()
    
    # Create config file
    if mic_index is not None or input("\nSave configuration? (y/n): ").lower() == 'y':
        create_microphone_config(mic_index)
    
    print("\n👋 Microphone setup complete!")

if __name__ == "__main__":
    main()
