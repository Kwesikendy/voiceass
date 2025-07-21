import speech_recognition as sr
import pyttsx3
import requests
import json

# === Setup ===
recognizer = sr.Recognizer()
engine = pyttsx3.init()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"  # or your pulled model

# === Speak ===
def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

# === Listen ===
def listen():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        print("You:", command)
        return command
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError:
        speak("Sorry, speech service is down.")
        return ""

# === Call Ollama ===
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
                    print(text, end='', flush=True)
                    reply += text
            except json.JSONDecodeError:
                continue
    print()
    return reply

# === Main loop ===
def main():
    speak("Hello! I am your AI assistant. Say something!")
    while True:
        query = listen()
        if query == "":
            continue
        if any(x in query.lower() for x in ["bye", "stop", "exit"]):
            speak("Goodbye!")
            break

        answer = ask_ollama(query)
        speak(answer)

if __name__ == "__main__":
    main()
