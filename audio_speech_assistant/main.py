import speech_recognition as sr
from features import speak, tell_time, open_google, joke

recognizer = sr.Recognizer()

def listen():
    with sr.Microphone() as source:
        speak("I'm listening...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        command = command.lower()
        print("You said:", command)

        if "time" in command:
            tell_time()
        elif "google" in command:
            open_google()
        elif "joke" in command: 
            joke()
        else:
            speak("Sorry, I don't understand that yet.")

    except sr.UnknownValueError:
        speak("I couldn't understand you. Try again.")
    except sr.RequestError:
        speak("Network error.")

listen()
