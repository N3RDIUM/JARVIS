import speech_recognition as sr
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('JARVIS')
logger.setLevel(logging.INFO)

class BackgroundListener:
    def __init__(self, callback):
        self.callback = callback
        self.r = sr.Recognizer()
        self.m = sr.Microphone()
        with self.m as source:
            self.r.adjust_for_ambient_noise(source)
        self.stop = self.r.listen_in_background(self.m, self.callback.func)

class BackgroundListenerCallback:
    def __init__(self):
        self.funcs = []
    
    def add_func(self, function):
        self.funcs.append(function)

    def func(self, recognizer, audio):
        for function in self.funcs:
            function(recognizer, audio)
            
class Recognizer:
    def __init__(self):
        self.r = sr.Recognizer()
        self.listener_callback = BackgroundListenerCallback()
        self.listener_callback.add_func(self.on_speech)
        self.listener = BackgroundListener(self.listener_callback)
        
    def add_callback(self, function):
        self.listener_callback.add_func(function)
        
    def on_speech(self, recognizer, audio):
        try:
            text = recognizer.recognize_google(audio)
            logger.info('Recognized: {}'.format(text))
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            logger.info('Could not request results from Google Speech Recognition service; {0}'.format(e))