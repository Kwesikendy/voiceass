import pyttsx3

def list_voices():
    """List all available voices on the system"""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    
    print("🎤 Available voices on your system:")
    print("=" * 50)
    
    for i, voice in enumerate(voices):
        print(f"{i + 1}. {voice.name}")
        print(f"   ID: {voice.id}")
        print(f"   Age: {getattr(voice, 'age', 'Unknown')}")
        print(f"   Gender: {getattr(voice, 'gender', 'Unknown')}")
        print(f"   Languages: {getattr(voice, 'languages', ['Unknown'])}")
        print("-" * 30)
    
    engine.stop()

if __name__ == "__main__":
    list_voices()
