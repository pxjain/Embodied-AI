import json
import vosk
import pyaudio
import time
import speech_recognition as sr
from openai import OpenAI
import pyttsx3

# VOSK model path
MODEL_PATH = r"C:\Users\Student\Documents\Project\VOSK Models\vosk-model-en-us-0.22"

recognizer_choice = recognizer_choice = input("Type 'v' for Vosk or 'g' for Google Speech Recognition: ").strip().lower()


# ChatGPT API setup
client = OpenAI(api_key='')  # Replace with your API key
MODEL = "gpt-4o"

# Initialize TTS
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Function to convert text to speech
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to send text to ChatGPT API
def send_to_chatgpt(text):
    print("Data has been sent to GPT:", text)
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are Kermit the Frog, a friendly character who responds in an entertaining and engaging way, keeping responses concise."},
            {"role": "user", "content": text}
        ]
    )
    if completion.choices:
        response = completion.choices[0].message.content
        if response:  # Check if the response is not empty
            print("CHATGPT:", response)
            speak(response)
        else:
            print("CHATGPT: No response received.")
    else:
        print("CHATGPT: No choices found in the response.")

# List of possible variations that Vosk might interpret as "Dr. Spot"
trigger_phrases = ["dr. spot", "doctor spot", "dr spot", "doctor. spot"]

# Function to check for the trigger phrase and extract the relevant command text
def extract_command(text):
    lower_text = text.lower()
    for phrase in trigger_phrases:
        if phrase in lower_text:
            command_text = lower_text.split(phrase, 1)[1].strip()
            return command_text if command_text else None
    return None

# Main transcription loop
try:
    if recognizer_choice == 'v':

        # Initialize VOSK model - STT
        model = vosk.Model(MODEL_PATH)
        vosk_recognizer = vosk.KaldiRecognizer(model, 16000)

        # Initialize PyAudio for audio input
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=16384)
        stream.start_stream()
        
        print("Vosk:Listening")

        while True:
            data = stream.read(4096, exception_on_overflow=False)
            if vosk_recognizer.AcceptWaveform(data):
                result = json.loads(vosk_recognizer.Result())
                text = result.get('text', '')
                if text:
                    print(f"You said: {text}")
                    command_text = extract_command(text)
                    if command_text:
                        print(f"Sending to ChatGPT: {command_text}")
                        send_to_chatgpt(command_text)

    elif recognizer_choice == 'g':
        r = sr.Recognizer()
        print("GR: Listening...")

        # Listen for a single command and return control to the main loop
        while True:
            with sr.Microphone() as source:
                r.pause_threshold = 3  # Increase pause threshold
                r.energy_threshold = 300  # Adjust for ambient noise

                try:
                    audio = r.listen(source, timeout=None)  # Continuously listen
                    text = r.recognize_google(audio, language='en-IN')
                    print(f"You said: {text}")

                except sr.UnknownValueError:
                    print("Sorry, I could not understand the audio. Please try again.")
                except sr.RequestError:
                    print("Could not request results from Google Speech Recognition service.")
                except KeyboardInterrupt:
                    print("\nStopping...")
                    break  # Break the loop if user interrupts

                command_text = extract_command(text)
                if command_text:
                    print(f"Sending to ChatGPT: {command_text}")
                    send_to_chatgpt(command_text)

except KeyboardInterrupt:
    print("Stopping...")

finally:
    # Only close stream and audio if Vosk was selected and stream was initialized
    if recognizer_choice == 'v' and stream is not None:
        stream.stop_stream()
        stream.close()
        audio.terminate()