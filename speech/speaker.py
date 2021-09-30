# imports
import os
import shutil

import numpy as np
import playsound
import scipy.io.wavfile as wavf
import torch
from gtts import gTTS

# set the device to CPU
device = torch.device('cpu')


class Speaker():
    def __init__(self):
        self.initialized = False
        self.speaking = False

    def initialize(self):
        self.SAVE_PATH = "speech_tts/"

        try:
            # check if the folder exists and delete it
            shutil.rmdir(self.SAVE_PATH)
            # create the folder again
            os.mkdir(self.SAVE_PATH)
        except:
            try:
                # first time initialization
                os.mkdir(self.SAVE_PATH)
            except:
                pass
        
        # get the pytorch model
        language = 'en'
        speaker = 'lj_16khz'
        model, symbols, sample_rate, example_text, apply_tts = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                                                            model='silero_tts',
                                                                            language=language,
                                                                            speaker=speaker)
        self.model = model
        self.symbols = symbols
        self.sample_rate = sample_rate
        self.apply_tts = apply_tts
        self.initialized = True
        self.SPOKEN = 0

    def speak_gtts(self, text):
        speech = gTTS(text)
        speech.save(self.SAVE_PATH+"_.mp3")
        playsound.playsound(self.SAVE_PATH+"_.mp3")
        os.remove(self.SAVE_PATH+"_.mp3")

    def speak_silero(self, text):
        self.model = self.model.to(device) 

        audio = self.apply_tts(texts=[str(text)],
                               model=self.model,
                               sample_rate=self.sample_rate,
                               symbols=self.symbols,
                               device=device)
        fs = 16000
        out_f = self.SAVE_PATH+str(self.SPOKEN)+'.wav'

        wavf.write(out_f, fs, np.array(audio[0]))
        playsound.playsound(self.SAVE_PATH+str(self.SPOKEN)+'.wav')
        self.SPOKEN += 1

def test():
    speaker = Speaker()
    speaker.initialize()
    while True:
        let = input('> ')
        speaker.speak_silero(let)
        speaker.speak_gtts(let)

# test
# test()