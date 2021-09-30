# imports
import os
import shutil
from glob import glob

import speech_recognition as sr
import torch

device = torch.device('cpu')  # gpu also works, but our models are fast enough for CPU

model, decoder, utils = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                       model='silero_stt',
                                       language='en', # also available 'de', 'es'
                                       device=device)
(read_batch, split_into_batches,
 read_audio, prepare_model_input) = utils  # see function signature for details


class Recognizer():
    def __init__(self):
        self.r = sr.Recognizer()
        self.m = sr.Microphone()
        self.NUMBER_OF_SPEECHES = 0
        self.initialized = False
        self.stopped = False
        self.wake = False

    def initialize(self):
        with self.m as source:
            self.r.adjust_for_ambient_noise(source)
        
        self.SAVE_PATH = "speech_stt/"

        try:
            shutil.rmdir(self.SAVE_PATH)
            os.mkdir(self.SAVE_PATH)
        except:
            try:
                os.mkdir(self.SAVE_PATH)
            except:
                pass
        
        self.initialized = True
        
    def recognize_from_mic(self):
        if self.initialized:
            file = self.listen_and_save() 
            return self.recognize_from_file(file)
        else:
            print("Please initialize the recognizer first.")

    def recognize_from_file(self, file_path):
        if self.initialized:
            try:
                try:
                    file = sr.AudioFile(file_path)
                    with file:
                        audio = self.r.record(file)
                        return self.r.recognize_google(audio)
                except sr.UnknownValueError:
                    return ""
            except:
                self.recognize_from_file_offline(file_path)
        else:
            print("Please initialize the recognizer first.")

    def listen_and_save(self):
        if self.initialized:
            with self.m as source:
                self.r.adjust_for_ambient_noise(source)
                audio = self.r.listen(source)
            with open(self.SAVE_PATH + str(self.NUMBER_OF_SPEECHES) + ".wav", "wb") as f:
                f.write(audio.get_wav_data())
            self.NUMBER_OF_SPEECHES += 1
            return self.SAVE_PATH + str(self.NUMBER_OF_SPEECHES-1) + ".wav"
        else:
            print("Please initialize the recognizer first.")

    def recognize_from_file_offline(self, file_path):
        if self.initialized:
            files = glob(file_path)
            batches = split_into_batches(files, batch_size=10)
            input = prepare_model_input(read_batch(batches[0]),
                                        device=device)

            output = model(input)
            for _ in output:
                print(decoder(_.cpu()))
        else:
            print("Please initialize the recognizer first.")

    def adjust_mic(self):
        if self.initialized:
            with self.m as source:
                self.r.adjust_for_ambient_noise(source)
        else:
            print("Please initialize the recognizer first.")

def test():
    print('Speak something:')
    rec = Recognizer()
    rec.initialize()
    while True:
        print(rec.recognize_from_mic(),end=' ')

# test
# test()
