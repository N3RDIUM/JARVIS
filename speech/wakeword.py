#!/usr/bin/env python3
#Porcupine wakeword includes
import struct
import pyaudio
import pvporcupine

porcupine = None
pa = None
audio_stream = None

class WakeWord():
    def __init__(self):
        self.wake = True
        
    def start_listening(self):
        porcupine = pvporcupine.create(keywords=["jarvis"], access_key="K8MvQn5Ad6P4vIFyb9C93NkWIU3Lm2lYH+SW0tXP5eoYtWAaWIz01g==")

        pa = pyaudio.PyAudio()

        audio_stream = pa.open(
                        rate=porcupine.sample_rate,
                        channels=1,
                        format=pyaudio.paInt16,
                        input=True,
                        frames_per_buffer=porcupine.frame_length)

        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)

            if keyword_index >= 0:
                print("<< wake >>")
                self.wake = True
                break

def test():
    print('Speak jarvis:')
    while True:
        try:
            w = WakeWord()
            w.start_listening()
        except:
            print('<< :END >>')
            break

# test
# test()