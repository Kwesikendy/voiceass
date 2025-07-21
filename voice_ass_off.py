from vosk import Model, KaldiRecognizer
import pyaudio
import pyttsx3
import json
import requests


model = Model("path/to/vosk-model")  
rec = KaldiRecognizer(model, 16000)
engine = pyttsx3.init()

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

def listen():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1,
                    rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    print("Listening...")
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if rec.AcceptWaveform(data):
            result = rec.Result()
            try:
                result_data = json.loads(result)
                text = result_data.get('text', '')
                if text.strip():  # Only return if there's actual text
                    print("You:", text)
                    return text
            except json.JSONDecodeError:
                continue

# === Ollama Integration ===
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"  # or your pulled model

def ask_ollama(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt
    }
    response = requests.post(OLLAMA_URL, json=payload, stream=True)
    
    reply = ""
    for line in response.iter_lines():
        if line:
            data = line.decode('utf-8')
            try:
                if data.startswith('{') and 'response' in data:
                    json_data = json.loads(data)
                    text = json_data.get('response', '')
                    reply += text
            except json.JSONDecodeError:
                continue
    return reply

# === Main loop ===
def main():
    speak("Hello! I am your offline AI assistant. Say something!")
    while True:
        query = listen()
        if query and query.strip():
            if any(x in query.lower() for x in ["bye", "stop", "exit"]):
                speak("Goodbye!")
                break
            
            answer = ask_ollama(query)
            speak(answer)

if __name__ == "__main__":
    main()
