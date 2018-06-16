import json
import logging as log
import time

from shove import Shove

with open('config.json') as json_data_file:
    config = json.load(json_data_file)
    config_shove = config.get("shove")
    config_lda = config.get("lda")
    shove_buffer = config_shove.get("buffer", 10)
    shove_folder = config_shove.get("folder_path", "./")
    results_path = config.get("classification_output_file", "./classification_results")
    if config.get("verbose", False):
        log.basicConfig(format="%(message)s", level=log.INFO)

articles_dict = Shove("file://" + shove_folder + "/articles", sync=shove_buffer)
titles_dict = Shove("file://" + shove_folder + "/titles", sync=shove_buffer)
words_dict = Shove("file://" + shove_folder + "/words", sync=shove_buffer)
R_w_dict = Shove("file://" + shove_folder + "/R_w", sync=shove_buffer)
vocabulary_c_dict = Shove("file://" + shove_folder + "/vocabulary_c", sync=shove_buffer)

words_set = set(words_dict)


def clasify_topic(topic, topic_id, num_results=10):
    log.info("[%s] Filtering words", topic_id)
    words_topic, words_weight_dict = prepare_words(topic)
    log.info("[%s] w->t", topic_id)
    w_supports_t = calculate_w_supports_t_and_S_t(words_topic)
    log.info("[%s] B_c", topic_id)
    B_c_dict = calculate_B_c(w_supports_t)
    log.info("[%s] R_t", topic_id)
    R_t_dict = calculate_R_t(w_supports_t, words_weight_dict)
    log.info("[%s] R_a", topic_id)
    R_a_dict = calculate_R_a(R_t_dict)
    log.info("[%s] R_c", topic_id)
    R_c_dict = calculate_R_c(R_a_dict, B_c_dict)

    log.info("[%s] R_c_prime", topic_id)
    R_c_list = sorted(list(R_c_dict.items()), key=lambda x: x[1], reverse=True)
    d_w_dict = create_d_w(words_set)
    R_c_prime_list = []
    for R_c in R_c_list:
        R_c_prime_list.append(recalculate_R_c(R_c, B_c_dict.get(R_c[0]), d_w_dict))

    result = sorted(R_c_prime_list, key=lambda x: x[1], reverse=True)[0:num_results]
    print("[", topic_id, "] Classification: ", result)
    log.info("[%s] Words unfiltered: %s", topic_id, topic)
    log.info("[%s] Words filtered (%d): %s", topic_id, len(words_topic), words_topic)

    return result


def calculate_w_supports_t_and_S_t(words_topic):
    words_topic_set = set(words_topic)
    w_supports_t = {}
    for word in words_topic:
        word_entry = words_dict.get(word)
        for title_id in word_entry:
            title_entry = titles_dict.get(title_id)
            if len(title_entry.words) == 1:
                w_supports_t[(word, title_id)] = 1
            else:
                S_t = len(title_entry.words.intersection(words_topic_set))
                if S_t >= len(title_entry.words) - 1:
                    w_supports_t[(word, title_id)] = S_t
    return w_supports_t


def calculate_R_t(w_supports_t, words_weight_dict):
    R_t_dict = {}
    for w_t in w_supports_t:
        word = w_t[0]
        title_id = w_t[1]
        title_entry = titles_dict.get(title_id)
        w_w = words_weight_dict.get(word, 1)
        R_w = R_w_dict.get(word)
        t_w = len(words_dict.get(word))
        a_t = len(title_entry.articles)
        S_t = w_supports_t.get(w_t)
        L_t = len(title_entry.words)
        R_t = R_t_dict.get(title_id, 0)

        value = R_t + (w_w * R_w * (1 / t_w) * (1 / a_t) * (S_t / L_t))
        R_t_dict[title_id] = value
    return R_t_dict


def calculate_R_a(R_t_dict):
    R_a_dict = {}
    for title_id in R_t_dict:
        R_t = R_t_dict.get(title_id)
        title_entry = titles_dict.get(title_id)
        for article in title_entry.articles:
            R_a = R_a_dict.get(article, 0)
            if R_t > R_a:
                R_a = R_t
            R_a_dict[article] = R_a
    return R_a_dict


def calculate_B_c(w_supports_t):
    B_c_dict = {}
    for w_t in w_supports_t:
        word = w_t[0]
        title_id = w_t[1]
        title_entry = titles_dict.get(title_id)
        for article in title_entry.articles:
            article_entry = articles_dict.get(article)
            for category in article_entry.categories:
                B_c = B_c_dict.get(category, set())
                B_c.add(word)
                B_c_dict[category] = B_c
    return B_c_dict


def calculate_R_c(R_a_dict, B_c_dict):
    R_c_dict = {}
    for article in R_a_dict:
        article_entry = articles_dict.get(article)
        R_a = R_a_dict.get(article)
        for category in article_entry.categories:
            R_c = R_c_dict.get(category, 0)
            R_c_dict[category] = R_c + R_a
    for category in R_c_dict:
        R_c = R_c_dict.get(category, [])
        v_c = len(B_c_dict.get(category, []))
        d_c = len(vocabulary_c_dict.get(category, []))
        if d_c == 0:
            R_c_dict[category] = 0
        else:
            R_c_dict[category] = (v_c / d_c) * R_c
    return R_c_dict


def create_d_w(words):
    d_w_dict = {}
    for word in words:
        d_w_dict[word] = 1
    return d_w_dict


def recalculate_R_c(R_c, B_c, d_w_dict):
    sumatory = 0
    for word in B_c:
        d_w = d_w_dict.get(word)
        sumatory += d_w
        d_w_dict[word] = d_w / 2
    return (R_c[0], R_c[1] * (float(sumatory) / float(len(B_c))))


def prepare_words(topic):
    words_tuples = [word for word in topic if word[0] in words_set]
    words_weight_dict = {}
    words_topic = []
    for tuple in words_tuples:
        word = tuple[0]
        weight = float(tuple[1])
        words_weight_dict[word] = weight
        words_topic.append(word)
    return words_topic, words_weight_dict


def classify_topics(topics_dict):
    results_dict = {}
    file = open(results_path, "w")
    for topic in topics_dict:
        results = clasify_topic(topics_dict.get(topic), topic)
        results_dict[topic] = results
        file.write(str.format("{}; {}\n", str(topic), str(results)))
    file.close()
    return results_dict



if __name__ == "__main__":
    start_time = time.time()
    with open(config_lda.get("output_file", "./topics_results.json")) as json_data_file:
        topics_dict = json.load(json_data_file)
    classify_topics(topics_dict)
    print("Execution time took %.3f seconds" % (time.time() - start_time))
