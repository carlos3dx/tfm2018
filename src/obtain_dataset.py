import json
import logging as log
import re
import time
import xml.etree.ElementTree as ET

import os

from src.clean_text import clean_text_list

with open('config.json') as json_data_file:
    config = json.load(json_data_file)
    config_pp = config.get("preprocess")
    if config.get("verbose", False):
        log.basicConfig(format="%(message)s", level=log.INFO)

p_nonword = re.compile(r'\W')



def process_articles(file_path):
    redirect_dict = {}
    file = open(file_path + "_temp", "w")
    pages = 0
    p_category = re.compile(r"\[\[Category:([^\]]*)\]\]")
    p_redirect = re.compile(r"#REDIRECT\ ?\[\[([^\]]*)\]\]")

    lines = []

    for event, elem in ET.iterparse(config_pp.get("articles_path"), events=('start', 'end')):
        if event == "end" and elem.tag.endswith('page'):
            article_categories = []
            for item in list(elem):
                if item.tag.endswith('title'):
                    article_title = item.text
                elif item.tag.endswith('ns'):
                    article_ns = item.text
                    if article_ns != "0":
                        break
                elif item.tag.endswith('id'):
                    article_id = item.text
                elif item.tag.endswith('revision'):
                    for sub_item in list(item):
                        if sub_item.tag.endswith('text'):
                            article_text = sub_item.text

            if article_ns == "0":
                for match in re.finditer(p_category, article_text):
                    article_categories.append(match.group(1))

            if article_categories:
                lines.append(process_article(article_id, article_title, article_text, article_categories))
                redirections = redirect_dict.pop(article_title, [])
                for redirection in redirections:
                    lines.append(process_article(article_id, redirection, article_text, article_categories))

            elif "REDIRECT" in article_text:
                destinations = []
                for match in re.finditer(p_redirect, article_text):
                    destinations.append(match.group(1))
                for destination in destinations:
                    entry = redirect_dict.get(destination, [])
                    entry.append(article_title)
                    redirect_dict[destination] = entry

            elem.clear()
            pages += 1
            # print(pages)

            if pages % 10000 == 0:
                file.writelines(lines)
                print("Processed pages = ", pages)
                lines = []

    print("Total pages processed = ", pages)
    log.info("Closing temp file")
    file.writelines(lines)
    file.close()

    print("Writting dataset")
    output_file = open(file_path, "w")
    lines = []
    with open(file_path + "_temp", "r") as temp_file:
        for line in temp_file:
            lines.append(line)
            items = line[:-1].split(";")
            line_title = items[1]
            redirections = redirect_dict.pop(line_title, [])
            for redirection in redirections:
                lines.append(process_article(items[0], redirection, items[2], items[3]))
            if len(lines) >= 100000:
                output_file.writelines(lines)
                lines = []

    output_file.writelines(lines)
    output_file.close()
    try:
        os.remove(file_path + "_temp")
    except OSError:
        pass


def process_article(id, title, text, categories):
    text_clean = clean_text_list(text)
    increment = 1 / len(text_clean)
    tf_dict = {}
    for term in text_clean:
        tf = tf_dict.get(term, 0)
        tf += increment
        tf_dict[term] = tf
    return str.join(";", [id, title, str([(x, tf_dict.get(x)) for x in tf_dict]), str(categories)]) + "\n"


if __name__ == "__main__":
    start_time = time.time()
    process_articles(config_pp.get("dataset_file", "./dataset"))
    print("Execution time took %.3f seconds" % (time.time() - start_time))
