#imports
import os
import time
import playsound
import pyautogui
import wolframalpha 
from gtts import gTTS
import pywhatkit as player
from datetime import datetime
import speech_recognition as sr
from random import * 
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import nltk
nltk.download('punkt')
nltk.download('nps_chat')
posts = nltk.corpus.nps_chat.xml_posts()[:10000]


def dialogue_act_features(post):
    features = {}
    for word in nltk.word_tokenize(post):
        features['contains({})'.format(word.lower())] = True
    return features

featuresets = [(dialogue_act_features(post.text), post.get('class')) for post in posts]
size = int(len(featuresets) * 0.1)
train_set, test_set = featuresets[size:], featuresets[:size]
classifier = nltk.NaiveBayesClassifier.train(train_set)

chatbot = ChatBot('Pion')

trainer = ChatterBotCorpusTrainer(chatbot)

trainer.train("chatterbot.corpus.english")

print("__________")

app_id = "E46YXW-T5LG6RT7K7"
client = wolframalpha.Client(app_id) 
r = sr.Recognizer()
m = sr.Microphone()
with m as source:
    r.adjust_for_ambient_noise(source)

words = []
aggree = ["OK!","Sure!","Sure thing!","here you go!"]
ap = ["Sorry! I can't do that.","I dont know the answer to that one!","can you  say that again?","sorry, I don't know what you're talking about."]

#define a recognizer class to recognize speech
class recognizer():
    def __init__(self):
        #Microphone and Recognizer objects
        self.mic = sr.Microphone()
        self.recognizer = sr.Recognizer()
        #language and spoken words list
        self.lang = ""
        self.said = ""
        with self.mic as mic:
            self.recognizer.adjust_for_ambient_noise(mic,duration=0.5)

    def recognize(self,audio,lang="en-IN"):
        #print('rec')
        #recognise the speech from audio
        self.recognizer.adjust_for_ambient_noise(self.mic,duration=0.5)
        try:
            self.spoken = self.recognizer.recognize_google(audio,language=str(lang))
        except:
            return None
        return self.spoken

    def recognize_from_mic(self,lang="en-IN"):
        #recognise the speech directly from the mic
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("say:",end=" ")
            r.adjust_for_ambient_noise(source)
            self.audio = r.listen(source)
            self.said = ""

            try:
                self.said = r.recognize_google(self.audio)
                print(self.said)
                
            except Exception as e:
                print("",end="")

        return self.said
        

class tts():
    def __init__(self):
        self.speaking = False

    def speak_gtts(self,word):
        self.word = gTTS(word)
        self.word.save("_.mp3")
        self.speaking = True
        self.speaking = playsound.playsound("_.mp3")
        os.remove("_.mp3")


class response():
    def __init__(self):
        self.dictating = False
        self.playing = False
        self.wake = False
        self.chatterbot_response = ''
        self.chatterbot_said = False

    def respond(self,word):
        self.chatterbot_said = False
        if "play" in word:
            if word.replace("play","") == "":
                speaker.speak_gtts("what shall I play?")
                play = rec.recognize_from_mic()
                speaker.speak_gtts(aggree[randint(0,len(aggree)-1)]+" playing "+play)
                player.playonyt(play)
                self.playing = True

            else:
                speaker.speak_gtts(aggree[randint(0,len(aggree)-1)]+" playing "+word.replace("play",""))
                player.playonyt(word.replace("play",""))
                self.playing = True

        elif "search" in word:
            speaker.speak_gtts(aggree[randint(0,len(aggree)-1)])
            if word.replace("search","") == "":
                speaker.speak_gtts("what shall I search?")
                search = rec.recognize_from_mic()
                speaker.speak_gtts(aggree[randint(0,len(aggree)-1)]+" searching "+search)
                player.search(search)

            else:
                speaker.speak_gtts(aggree[randint(0,len(aggree)-1)]+" searching "+word.replace("search",""))
                player.search(word.replace("search",""))

        elif "dicta" in word:
            if "stop" in word:
                self.dictating=False

            elif "start" in word:
                speaker.speak_gtts(aggree[randint(0,len(aggree)-1)]+"starting dictation.")
                while True:
                    self.dict=rec.recognize_from_mic()
                    if not self.dict == "stop dictating":
                        self.dictating=True
                        print("__dict__")
                        print(self.dict)
                        pyautogui.typewrite(self.dict+" ",0)

                    if self.dict == "stop dictating":
                        self.dictating=False
                        break

        elif "open" in word:
            if "Word" in word:
                speaker.speak_gtts(aggree[randint(0,len(aggree)-1)]+" opening word")
                os.system('WINWORD')

            elif "PowerPoint" in word:
                speaker.speak_gtts(aggree[randint(0,len(aggree)-1)]+" opening powerpoint")
                os.system('POWERPNT')

            elif "Access" in word or "access" in word:
                speaker.speak_gtts(aggree[randint(0,len(aggree)-1)]+" opening access")
                os.system('MSACCESS')

            elif "Excel" in word:
                speaker.speak_gtts(aggree[randint(0,len(aggree)-1)]+" opening excel")
                os.system('EXCEL')

            elif "Publisher" in word:
                speaker.speak_gtts(aggree[randint(0,len(aggree)-1)]+" opening publisher")
                os.system('MSPUB')

            elif "Onenote" in word:
                speaker.speak_gtts(aggree[randint(0,len(aggree)-1)]+" opening onenote")
                os.system('ONENOTE')

            elif "Outlook" in word:
                speaker.speak_gtts(aggree[randint(0,len(aggree)-1)]+" opening outlook mail")
                os.system('OUTLOOK')

            elif "Notepad" in word:
                speaker.speak_gtts(aggree[randint(0,len(aggree)-1)]+" opening notepad")
                os.system('notepad')

            else:
                pass

        elif "time" in word:
            self.time = datetime.now()
            speaker.speak_gtts("it is"+str(time.strftime("%H:%M")))

        elif "pause" in word:
            speaker.speak_gtts(aggree[randint(0,len(aggree)-1)])
            if self.playing == True:
                pyautogui.press('playpause')
                self.playing = False

        elif "play" in word:
            speaker.speak_gtts(aggree[randint(0,len(aggree)-1)])
            if self.playing == False:
                pyautogui.press('playpause')
                self.playing = True

        elif "shutdown" in word:
            speaker.speak_gtts(aggree[randint(0,len(aggree)-1)])
            os.system("shutdown /s /t 1")

        elif "hibernate" in word:
            speaker.speak_gtts(aggree[randint(0,len(aggree)-1)])
            os.system("shutdown.exe /h")

        elif "sleep" in word:
            speaker.speak_gtts(aggree[randint(0,len(aggree)-1)])
            pyautogui.hotkey('fn','f1')

        elif word == "":
            speaker.speak_gtts("please say that again")
            while True:
                word = rec.recognize_from_mic()
                playsound.playsound("coin.mp3")
                if word == "":
                    speaker.speak_gtts("please say that again")
                    playsound.playsound("coin.mp3")

                elif word != "":
                    playsound.playsound("coin.mp3")
                    break
        else:
            rand = randint(0,1)
            self.chatterbot_response = chatbot.get_response(word)
            self.chatterbot_said = True
            print('chatterbot says: '+str(self.chatterbot_response))
            if rand == 0:
                try:
                    res = client.query(word)
                    answer = next(res.results).text
                    if len(answer) < 50:  
                        speaker.speak_gtts(answer)
                    else:
                        # deliberately give an error and throw it to the chatterbot instance
                        print('throwing to chatbot...')
                        raise Exception
                    
                except:
                    speaker.speak_gtts(str(self.chatterbot_response))
            else:
                speaker.speak_gtts(str(self.chatterbot_response))

        if self.chatterbot_said:
            data = classifier.classify(dialogue_act_features(str(self.chatterbot_response)))
            print('chatterbot response type: '+str(data))
            if 'Question' in data:
                self.wake = True
                self.chatterbot_said = False
        else:
            self.wake = False
        print('_____')

print("__________")
rec = recognizer()
speaker = tts()
resp = response()

def callback(recognizer, audio, resp, rec):
    with rec.mic as source:
        recognizer.adjust_for_ambient_noise(source,duration=0.5)
    try:
        spoken = rec.recognizer.recognize_google(audio,language=str('en-IN'))
        if "computer" in spoken and not resp.wake:
            print("<< wake >>")
            resp.wake = True
            return spoken
    except:
        return None

print("__________")
bg = r.listen_in_background(m,lambda recognizer, audio: callback(recognizer, audio, resp, rec))
print(":initialisation_successful:")

if __name__ == "__main__":
    playsound.playsound("coin.mp3")
    with rec.mic as source:
        rec.recognizer.adjust_for_ambient_noise(source,duration=0.5)
    while True:
        if resp.wake:
            playsound.playsound("coin.mp3")
            word = rec.recognize_from_mic()
            #print(word)
            playsound.playsound("coin.mp3")
            resp.respond(word)
