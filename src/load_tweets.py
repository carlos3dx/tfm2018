import json
import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

def load_tweets(file_path):
    with open(file_path, 'r') as file:
        tweets = json.load(file)

    p_rt_via = re.compile(r'(RT|via)((?:\b\W*@\w+)+)')
    p_user = re.compile(r'@\w+')
    p_punct_digit = re.compile(r'([\W_]+|\d+)')
    p_url = re.compile(r'http\w*\S+')
    p_reduce_whitespaces = re.compile(r'\s{2,}')
    p_whitespaces_removal = re.compile(r'(^\s|\s$)')
    result = []

    stops = set(stopwords.words("english"))
    stemmer = SnowballStemmer("english")
    for tweet in tweets:
        # print(tweet['text'])
        text = tweet['text']
        text = re.sub(p_rt_via, " ", text)
        text = re.sub(p_url, " ", text)
        text = re.sub(p_user, " ", text)
        text = re.sub(p_punct_digit, " ", text)
        text = re.sub(p_reduce_whitespaces, " ", text)
        text = re.sub(p_whitespaces_removal, "", text)
        text = text.lower()
        text_words = text.split(" ")
        text_words = [stemmer.stem(word) for word in text_words if word not in stops and len(word) > 0]
        result.append(text_words)

    return result