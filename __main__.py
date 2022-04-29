# imports
from regex import R
from __init__ import *
from speech import recognizer, speaker
import logging
import random

logging.basicConfig(level=logging.INFO)


def log(source, message):
    logging.info(f'[{source}]: {message}')


log('APP', 'Starting initialization...')


log('APP', 'Other imports were successful!')


class Response:
    def __init__(self):
        self.dictating = False
        self.apologies = ['Sorry, but I can\'t do that', 'Sorry, I don\'t understand.', 'Sorry, I cannot do that.', "Sorry! I can't do that.",
                          "I dont know the answer to that one!", "Can you please say that again?", "Sorry, I don't know what you're talking about."]
        self.aggree = ["OK!", "Sure!", "Sure thing!", "here you go!"]
        self._dictation = Dictation()

    def get_response(self, query):
        log('APP', f'Getting response for \'{query}\' ...')
        if 'joke' in query:
            return get_joke()
        elif 'open' in query:
            return random.choice(self.apologies)
        elif 'date' in query:
            return 'Today is: '+get_date()
        elif 'time' in query:
            return 'It is '+get_time()+' right now.'
        elif 'shutdown' in query:
            shutdown()
            return self.aggree[random.randint(0, len(self.aggree)-1)]
        elif 'restart' in query:
            restart()
            return self.aggree[random.randint(0, len(self.aggree)-1)]
        elif 'lock' in query or 'logout' in query or 'log out' in query or 'signout' in query or 'sign out' in query:
            logoff()
            return self.aggree[random.randint(0, len(self.aggree)-1)]
        elif 'dicta' in query and 'start' in query:
            self.dictating = True
            self._dictation.start()
            return self.aggree[random.randint(0, len(self.aggree)-1)]
        elif "search" in word:
            search(word.replace("search", ""))
            return self.aggree[random.randint(0, len(self.aggree)-1)]+f'Searching {word.replace("search","")}'
        elif "play" in word:
            search(word.replace("play", ""))
            return self.aggree[random.randint(0, len(self.aggree)-1)]+f'Playing {word.replace("play","")}'
        else:
            return 0


# train the chatbot
log('APP', 'Training ChatterBot...')
bot = Bot()
bot.train_corpus()
bot.train_with_inbuilt_data()

# make the wakeword object
log('APP', 'Initializing WakeWord engine...')
wake = WakeWord()

# make and train the recognizer and speaker
log('APP', 'Initializing speech utilities...')
_recognizer = Recognizer()
_speaker = Speaker()
_recognizer.initialize()
_speaker.initialize()

responder = Response()

log('APP', 'Initialization Successful. Say JARVIS to talk to JARVIS.')

def doIt(_ = False):
    if not _:
        wake.start_listening()
    word = _recognizer.recognize_from_mic()
    log('APP',f'You Said: {word}')
    try:
        response = responder.get_response(word)
    except:
        response = 0
    if not response == 0:
        log('APP', f'Response: {response}')
        _speaker.speak_silero(response)
    else:
        log('APP', 'No response found. Passing query to ChatterBot...')
        response = bot.get_response(word)
        log('APP', f'ChatterBot response: {response}')
        _speaker.speak_silero(response)
        if is_question(word):
            log('APP', 'Question detected. Responding with question...')
            doIt()

while True:
    doIt(False)
