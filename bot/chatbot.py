# imports
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer

import sys
import os
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'conversation_data')))

from data import ConversationData

class Bot():
    def __init__(self):
        # Create a new chat bot
        self.bot = ChatBot(
            'pion',
            storage_adapter='chatterbot.storage.SQLStorageAdapter',
            logic_adapters=[
                {
                    'import_path': 'chatterbot.logic.BestMatch'
                },
            ],
        )

        # Create the trainers
        self.list_trainer = ListTrainer(self.bot)
        self.corpus_trainer = ChatterBotCorpusTrainer(self.bot)

    def train_with_inbuilt_data(self):
        # Loop through the conversation data and train with each conversation
        for i in range(len(ConversationData)):
            self.list_trainer.train(ConversationData[i])
    
    def train_from_list(self, data):
        # Train the chat bot with a list of responses
        self.list.train(data)
    
    def train_corpus(self):
        # Train the chat bot with the english corpus
        self.corpus_trainer.train(
            'chatterbot.corpus.english'
        )

    def get_response(self, query):
        # Return the chat bot's response to a user's query
        return self.bot.get_response(query)

def test():
    bot = Bot()
    bot.train_with_inbuilt_data()
    bot.train_corpus()
    print('Start the conversaion')
    while True:
        query = input('You: ')
        response = bot.get_response(query)
        print('Bot: ', response)

# Test
# test()
