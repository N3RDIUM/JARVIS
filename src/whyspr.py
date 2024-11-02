import logging
import os
import time

import speech_recognition as sr
import torch
from faster_whisper import WhisperModel

from logger import logger

MODEL = "small.en"
logger.log(
    logging.DEBUG,
    f"DEBUG [whyspr   ]  Loading model `{MODEL}` for OpenAI Whisper...",
)
model = WhisperModel(MODEL, device="cpu", compute_type="int8")
pipeline = model.transcribe
logger.log(
    logging.DEBUG,
    f"DEBUG [whyspr   ]  Model `{MODEL}` loaded successfully!",
)


def recognize_from_mic():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("Say something!")
        audio = r.listen(source)

    with open("audio.wav", "wb") as f:
        f.write(audio.get_wav_data())
    print("Got it! Now to recognize it.")

    t = time.perf_counter()
    with torch.inference_mode():
        segments, info = pipeline("audio.wav", vad_filter=True)
    print(
        "Detected language '%s' with probability %f"
        % (info.language, info.language_probability)
    )
    recognized = ""
    for segment in segments:
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
        recognized += segment.text

    print(f"> {recognized}")
    print(f"Took {time.perf_counter() - t} seconds!")
    os.remove("audio.wav")

    return recognized
