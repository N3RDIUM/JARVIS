import requests
import playsound

def speak(text):
    speech_data = requests.post("http://localhost:8080/tts", json={
        "model": "en-us-ryan-medium.onnx",
        "input": text
    }).content
    with open(".cache/temp.wav", "wb") as f:
        f.write(speech_data)
    playsound.playsound(".cache/temp.wav")