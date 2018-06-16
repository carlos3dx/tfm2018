import json
import sys
import time

import gensim
import math

import numpy
from gensim import corpora

if sys.version_info < (3, 0):
    sys.stdout.write("Sorry, requires Python 3.x, not Python 2.x\n")
    sys.exit(1)

from load_tweets import load_tweets

with open('config.json') as json_data_file:
    config = json.load(json_data_file)
    config_lda = config.get("lda")
    reduce = config_lda.get("reduce_low_tfidf", False)


def main():
    tweets_path = config_lda.get("input_file")
    tweets_clean = load_tweets(tweets_path)

    dictionary = corpora.Dictionary(tweets_clean)
    dtm = [dictionary.doc2bow(text) for text in tweets_clean]
    if reduce:
        tweets_clean = remove_terms_low_median(tweets_clean, dictionary, dtm)
        # Calculate again
        dictionary = corpora.Dictionary(tweets_clean)
        dtm = [dictionary.doc2bow(text) for text in tweets_clean]

    k = config_lda.get("topics")
    if k == 0:
        k = calculate_num_topics()

    ldamodel = gensim.models.LdaMulticore(dtm, num_topics=k, id2word=dictionary,
                                          passes=config_lda.get("passes", 20))
    topics_dict = {}
    for topic in ldamodel.show_topics(formatted=False, num_topics=k, num_words=config_lda.get("words", 10)):
        topic_words = []
        for pair in topic[1]:
            topic_words.append((pair[0], str(pair[1])))
        topics_dict['topic_' + str(topic[0])] = topic_words

    file_system_json_file = open(config_lda.get("output_file", "./topics_results.json"), "w")
    file_system_json_file.write(json.dumps(topics_dict))
    file_system_json_file.close()


def calculate_num_topics():
    return 10


def remove_terms_low_median(tweets, dictionary, dtm):
    term_tfidf_dict = calculate_tfidf(dictionary, dtm)
    median = numpy.median(list(term_tfidf_dict.values()))
    tweets_clean = []
    for key in term_tfidf_dict:
        term_tf = term_tfidf_dict.get(key)
        if term_tf < median:
            term_tfidf_dict[key] = 0

    for tweet in tweets:
        new_tweet = [term for term in tweet if term_tfidf_dict.get(dictionary.token2id.get(term)) > 0]
        if len(new_tweet) > 0:
            tweets_clean.append(new_tweet)

    return tweets_clean


def calculate_tfidf(dictionary, dtm):
    term_tfidf_dict = {}

    term_tfs_dict = {}
    for doc in dtm:
        for x in doc:
            term_tfs = term_tfs_dict.get(x[0], [])
            term_tfs.append(calculate_tf(x[0], doc))
            term_tfs_dict[x[0]] = term_tfs

    for term in term_tfs_dict:
        term_tf = numpy.mean(term)
        term_tfidf_dict[term] = term_tf * calculate_idf(term, dictionary)
    return term_tfidf_dict


def calculate_tf(t, d):
    tf = 0
    num_terms = 0
    for x in d:
        num_terms += x[1]
        if x[0] == t:
            tf = x[1]
    return tf / num_terms


def calculate_idf(t, dictionary):
    return math.log(dictionary.num_docs / dictionary.dfs.get(t), 2)


def harmonic_mean(log_likelihood):
    ll_med = numpy.median(log_likelihood)
    return ll_med - math.log(numpy.mean([math.exp(-x + ll_med) for x in log_likelihood]))


if __name__ == '__main__':
    start_time = time.time()
    harmonic_mean([1, 1, 1])
    main()
    print("Execution time took %.3f seconds" % (time.time() - start_time))
    sys.exit(0)
