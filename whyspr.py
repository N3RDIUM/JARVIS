from faster_whisper import WhisperModel
import speech_recognition as sr
import torch
import time

model = WhisperModel("small.en", device="cpu", compute_type="int8")
pipeline = model.transcribe


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

    return recognized


recognize_from_mic()
