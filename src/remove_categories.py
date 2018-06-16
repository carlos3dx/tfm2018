import json
import logging as log
import time

from src.obtain_categories import obtain_categories

with open('config.json') as json_data_file:
    config = json.load(json_data_file)
    config_pp = config.get("preprocess")
    config_db = config.get("wiki_db")
    config_categories = config.get("categories")
    if config.get("verbose", False):
        log.basicConfig(format="%(message)s", level=log.INFO)


def clean_dataset(file_path):
    categories = obtain_categories(config_db.get("host"), config_db.get("db"), config_db.get("user"),
                                   config_db.get("passwd"),
                                   min=config_categories.get("articles_min"),
                                   max=config_categories.get("articles_max"))
    print("Writting dataset")
    output_file = open(file_path + "_clean", "w")
    lines = []

    with open(file_path, "r") as dataset:
        for line in dataset:
            parts = line.split(";")
            categories_part = parts[3][1:-2]
            categories_part = categories_part.replace("\'", "")
            list_categories_article = [category.strip() for category in categories_part.split(",")]
            article_categories = [category for category in list_categories_article if category in categories]
            if len(article_categories):
                lines.append(str.join(";", [parts[0], parts[1], parts[2], str(article_categories)]) + "\n")

            if len(lines) >= 100000:
                output_file.writelines(lines)
                lines = []

    output_file.writelines(lines)
    lines = []
    output_file.close()


if __name__ == "__main__":
    start_time = time.time()
    clean_dataset(config_pp.get("dataset_file", "./dataset"))
    print("Execution time took %.3f seconds" % (time.time() - start_time))
