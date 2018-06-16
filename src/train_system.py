import json
import logging as log
import math
import re
import time
from urllib.request import pathname2url

from shove import Shove

from Article import Article
from Title import Title
from clean_text import clean_text

with open('config.json') as json_data_file:
    config = json.load(json_data_file)
    config_shove = config.get("shove")
    config_db = config.get("wiki_db")
    config_categories = config.get("categories")
    shove_buffer = config_shove.get("buffer", 10)
    shove_folder = config_shove.get("folder_path", "./")
    dataset = config.get("train_dataset")
    if config.get("verbose", False):
        log.basicConfig(format="%(message)s", level=log.INFO)

articles_dict = Shove("file://" + shove_folder + "/articles", sync=shove_buffer)
titles_dict = Shove("file://" + shove_folder + "/titles", sync=shove_buffer)
words_dict = Shove("file://" + shove_folder + "/words", sync=shove_buffer)
categories_dict = {}
cf_w_dict = {}
R_w_dict = Shove("file://" + shove_folder + "/R_w", sync=shove_buffer)
vocabulary_c_dict = Shove("file://" + shove_folder + "/vocabulary_c", sync=shove_buffer)

lang = 'en'

p_nonword = re.compile(r'\W')


def process_articles():
    pages = 0
    # wiki_categories = obtain_categories(config_db.get("host"), config_db.get("db"), config_db.get("user"),
    #                                     config_db.get("passwd"),
    #                                     min=config_categories.get("articles_min"),
    #                                     max=config_categories.get("articles_max"))

    # file = open("./test_articles.txt", "w")
    with open(dataset, "r") as data:
        for line in data:
            elements = line.split(";")
            article_id = elements[0]
            article_title = elements[1]
            categories_part = elements[3][1:-2]
            categories_part = categories_part.replace("\'", "")
            article_categories = [category.strip() for category in categories_part.split(",")]
            # article_categories = [c for c in elements[3] if c in wiki_categories]

            if article_categories:
                article = Article(id=article_id, categories=article_categories)
                process_article(article, article_title)
                # linea = str.format("{} ; {} ; {}\n", article_title, str(clean_text(article_title)), str(article_categories))
                # file.write(linea)
                del article

            pages += 1
            if pages % 10000 == 0:
                print("Processed pages = ", pages)
    # file.close()

    # for event, elem in ET.iterparse(config.get("articles_path"), events=('start', 'end')):
    #     if event == "end" and elem.tag.endswith('page'):
    #         article_categories = []
    #         for item in list(elem):
    #             if item.tag.endswith('title'):
    #                 article_title = item.text
    #             elif item.tag.endswith('ns'):
    #                 article_ns = item.text
    #                 if article_ns != "0":
    #                     break
    #             elif item.tag.endswith('id'):
    #                 article_id = item.text
    #             elif item.tag.endswith('revision'):
    #                 for sub_item in list(item):
    #                     if sub_item.tag.endswith('text'):
    #                         article_text = sub_item.text
    #
    #         if article_ns == "0":
    #             for match in re.finditer(p_category, article_text):
    #                 if match.group(1) in wiki_categories:
    #                     article_categories.append(match.group(1))
    #
    #         if article_categories:
    #             article = Article(id=article_id, categories=article_categories)
    #             process_article(article, article_title)
    #             del article
    #
    #         elem.clear()
    #         pages += 1
    #
    #         if pages % 10000 == 0:
    #             print("Processed pages = ", pages)
    #
    # print("Total pages processed = ", pages)


def process_article(article, title):
    title_entry = process_title(title, article)
    if type(title_entry) == Title:
        for category in article.categories:
            add_article_to_category(article, category)
            for word in title_entry.words:
                add_w_to_vocabulary_c(word, category)

        if title_entry.id not in set(article.title_ids):
            article.add_title(title_entry.id)
        if article.id not in articles_dict or article != articles_dict.get(article.id):
            articles_dict[article.id] = article
    del article


def process_title(title, article):
    title_set = clean_text(title)

    id = frozenset_to_filename(frozenset(title_set))
    if len(id) >= 254 or len(pathname2url(id)) >= 254:
        return "error"
    else:
        try:
            title_entry = titles_dict.get(id, Title(id=id, words=title_set))
            if article.id not in set(title_entry.articles):
                title_entry.add_article(article.id)
                titles_dict[id] = title_entry

            add_title_to_words(title_entry)
            return title_entry
        except:
            return "error"


def add_title_to_words(title):
    for word in title.words:
        word_entry = words_dict.get(word, [])
        if title.id not in set(word_entry):
            word_entry.append(title.id)
            words_dict[word] = word_entry


def add_article_to_category(article, category):
    articles = categories_dict.get(category, [])
    if article.id not in set(articles):
        articles.append(article.id)
        categories_dict[category] = articles


def frozenset_to_filename(x):
    return re.sub(p_nonword, "_", str(x))


def calculate_cf_w():
    for word in words_dict:
        cf_w = set()
        word_entry = words_dict.get(word)
        for title in word_entry:
            title_entry = titles_dict.get(title)
            for article in title_entry.articles:
                article_entry = articles_dict.get(article)
                cf_w = cf_w.union(article_entry.categories)
        cf_w_dict[word] = len(cf_w)
        R_w_dict[word] = math.log(len(categories_dict) / len(cf_w), 2)


def add_w_to_vocabulary_c(word, category):
    words_c = vocabulary_c_dict.get(category, set())
    if word not in words_c:
        words_c.add(word)
        vocabulary_c_dict[category] = words_c


if __name__ == '__main__':
    start_time = time.time()
    print("Processing articles dataset")
    process_articles()
    log.info("Syncing articles dict")
    articles_dict.sync()
    log.info("Syncing title dict")
    titles_dict.sync()
    log.info("Syncing words dict")
    words_dict.sync()
    print("Calculating cf_w")
    calculate_cf_w()
    log.info("Closing articles dict")
    articles_dict.close()
    log.info("Closing titles dict")
    titles_dict.close()
    log.info("Closing words dict")
    words_dict.close()
    log.info("Syncing R_w dict")
    R_w_dict.sync()
    log.info("Syncing vocabulary_c dict")
    vocabulary_c_dict.sync()
    log.info("Closing R_w dict")
    R_w_dict.close()
    log.info("Closing vocabulary_c dict")
    vocabulary_c_dict.close()
    print("Execution time took %.3f seconds" % (time.time() - start_time))
