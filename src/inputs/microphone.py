import logging
import os
import threading
import time

import speech_recognition as sr
import torch
from faster_whisper import WhisperModel

from logger import logger

MODEL = "small.en"
logger.log(
    logging.DEBUG,
    f"DEBUG [ whyspr    ]  Loading OpenAI Whisper model `{MODEL}`...",
)
model = WhisperModel(MODEL, device="cpu", compute_type="int8")
pipeline = model.transcribe
logger.log(
    logging.DEBUG,
    f"DEBUG [ whyspr    ]  Model `{MODEL}` loaded successfully!",
)

r = sr.Recognizer()
m = sr.Microphone()
with m as source:
    logger.log(
        logging.INFO,
        "DEBUG [ whyspr    ]  Adjusting for ambient noise...",
    )
    r.adjust_for_ambient_noise(source)


def recognize_from_mic():
    with m as source:
        logger.log(
            logging.INFO,
            "DEBUG [ whyspr    ]  Listening...",
        )
        audio = r.listen(source)
        logger.log(
            logging.INFO,
            "DEBUG [ whyspr    ]  Audio capture complete! Recognizing...",
        )

    with open("audio.wav", "wb") as f:
        f.write(audio.get_wav_data())

    t = time.perf_counter()
    with torch.inference_mode():
        segments, info = pipeline("audio.wav", vad_filter=True)
    logger.log(
        logging.INFO,
        "DEBUG [ whyspr    ]  Detected language '%s' with probability %f"
        % (info.language, info.language_probability),
    )

    recognized = ""
    for segment in segments:
        logger.log(
            logging.INFO,
            "DEBUG [ whyspr    ]  [%.2fs -> %.2fs] %s"
            % (segment.start, segment.end, segment.text),
        )
        recognized += segment.text

    print(f"Took {time.perf_counter() - t} seconds!")
    os.remove("audio.wav")

    return recognized


class SpeechInput:
    name = "speech"

    def __init__(self, parent) -> None:
        self.parent = parent
        self.thread = threading.Thread(target=self.run)

    def run(self):
        logger.log(logging.INFO, "DEBUG [ whyspr    ]  Speech input stream started.")
        while True:
            recognized = recognize_from_mic()
            if recognized.strip() == "":
                continue
            self.parent.input_queue.append(recognized.strip())

    def begin_stream(self):
        self.thread.start()


input_export = SpeechInput
