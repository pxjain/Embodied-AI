#just testing
import json 
import vosk 
import pyaudio 
import requests 
import time

# VOSK model path 

#Accurate generic US English model
MODEL_PATH = r"C:\Users\Student\Documents\Project\VOSK Models\vosk-model-en-us-0.22" 
#Lightweight wideband model
# MODEL_PATH = r"C:\Users\Student\Documents\Project\VOSK Models\vosk-model-small-en-us-0.15" 


# Initialize VOSK model 

#Simple approach
model = vosk.Model(MODEL_PATH) 
recognizer = vosk.KaldiRecognizer(model, 16000)

#Try 1 - Optimize runtime by preloading
# model = None
# def get_model():
#     global model
#     if model is None:
#         try:
#             model = vosk.Model(MODEL_PATH)
#         except Exception as e:
#             print(f"Error loading Vosk model: {e}")
#             model = None
#     return model
# get_model()
# recognizer = vosk.KaldiRecognizer(model, 16000)
#End Try 1

#Try 2 - Optimize runtime by preloading
# class VoskRecognizer: 
#     _model = None 
#     _recognizer = None 

#     @classmethod 
#     def initialize(cls): 
#         if cls._model is None: 
#             cls._model = vosk.Model(MODEL_PATH) 
#             cls._recognizer = vosk.KaldiRecognizer(cls._model, 16000) 

#     @classmethod 
#     def get_recognizer(cls): 
#         if cls._recognizer is None: 
#             cls.initialize() 
#         return cls._recognizer 
#End Try 2


 
 

# Initialize PyAudio for audio input 
audio = pyaudio.PyAudio() 
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=16384) 
stream.start_stream() 
 

# ChatGPT API setup 
# CHATGPT_API_URL = "https://api.openai.com/v1/chat/completions" 
# API_KEY = "your_openai_api_key" 

# headers = { 
#     "Authorization": f"Bearer {API_KEY}", 
#     "Content-Type": "application/json", 
# } 
  
# Function to send text to ChatGPT API 
# def send_to_chatgpt(text): 
#     data = { 
#         "model": "gpt-3.5-turbo", 
#         "messages": [{"role": "user", "content": text}] 
#     } 
#     response = requests.post(CHATGPT_API_URL, headers=headers, data=json.dumps(data)) 
#     if response.status_code == 200: 
#         return response.json()["choices"][0]["message"]["content"] 
#     else: 
#         return "Error: Unable to process the request." 
 
#For ending timer if needed
silence_timeout = 10                #Roughly equal to second before ending
last_speech_time = time.time()      


# Real-time transcription and sending to ChatGPT 
try: 
    print("Listening...") 
    while True: 
        data = stream.read(4096, exception_on_overflow=False) 
        # recognizer = VoskRecognizer.get_recognizer()            #For test 2
        if recognizer.AcceptWaveform(data): 
            result = json.loads(recognizer.Result()) 
            text = result.get('text', '') 
            if text: 
                print(f"You said: {text}") 
                last_speech_time = time.time()

                # Send the transcribed text to ChatGPT API and get response 
                # response = send_to_chatgpt(text) 
                # print(f"ChatGPT: {response}") 
        
        #For ending timer if needed
        if time.time() - last_speech_time > silence_timeout:
            print("No speech detected for a while. Ending...")
            break

except KeyboardInterrupt: 
    print("Stopping...") 

finally: 
    stream.stop_stream() 
    stream.close() 
    audio.terminate() 

 