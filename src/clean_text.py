import re

import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

nltk.download('stopwords')

def clean_text(text, lang="english"):
    return set(clean_text_list(text, lang))

def clean_text_list(text, lang="english"):
    stops = set(stopwords.words(lang))
    stemmer = SnowballStemmer(lang)
    p_non_char = re.compile(r'\W|\d|_')
    p_reduce_whitespaces = re.compile(r'\s{2,')

    clean_text = re.sub(p_non_char, " ", text)
    clean_text = re.sub(p_reduce_whitespaces, " ", clean_text)
    clean_text = clean_text.lower()
    text_words = clean_text.strip().split(" ")
    return [stemmer.stem(word) for word in text_words if word not in stops and len(word) > 0]


#print(clean_text("hello my old friend"))