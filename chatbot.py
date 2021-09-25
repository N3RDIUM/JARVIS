from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import logging


'''
This is an example showing how to train a chat bot using the
ChatterBot Corpus of conversation dialog.
'''

# Enable info level logging
logging.basicConfig(level=logging.INFO)

chatbot = ChatBot('Example Bot')

# Start by training our bot with the ChatterBot corpus data
trainer = ChatterBotCorpusTrainer(chatbot)

trainer.train(
    'chatterbot.corpus.english'
)

while True:
    try:
        i = (input('>'))
        if not i == '':
            print(str(chatbot.get_response(i)))
        else:
            print('please provide input.')
    except:
        print('please provide input.')
