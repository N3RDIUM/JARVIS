# imports
import nltk

# download the required packages
nltk.download('punkt')
nltk.download('nps_chat')
posts = nltk.corpus.nps_chat.xml_posts()[:10000]

# Get the sentence type
def dialogue_act_features(post):
    features = {}
    for word in nltk.word_tokenize(post):
        features['contains({})'.format(word.lower())] = True
    return features
