import pyautogui
import speech_recognition as sr

class Dictation:
    def __init__(self):
        self.dictating = False
        self.mic = sr.Microphone()
        self.r = sr.Recognizer()
        self.stop_listening = None

    def start(self):
        self.dictating = True
        self.stop_listening = self.r.listen_in_background(self.mic, self.callback)
        print('Dictation Started!')
        
    def stop(self):
        self.dictating = False
        self.stop_listening()
        print('Dictation Stopped!')

    def callback(self, recognizer, audio):
        try:
            words = recognizer.recognize_google(audio)
            if not "stop" in words and not "dicta" in words and not 'jarvis' in words:
                print('You said: '+words)
                pyautogui.typewrite(words + ' ')
            else:
                self.stop()
        except:
            pass

def test():
    d = Dictation()
    d.start()
    while d.dictating:
        pass
    d.stop()

# test
# test()
