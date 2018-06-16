import json
import logging as log
import time

from clasify_topic import clasify_topic

with open('config.json') as json_data_file:
    config = json.load(json_data_file)
    config_pp = config.get("preprocess")
    if config.get("verbose", False):
        log.basicConfig(format="%(message)s", level=log.INFO)


def test_system(test_dataset):
    index = 0
    true_positives_global = 0
    false_positives_global = 0
    false_negatives_global = 0
    file_results = open("./test_results", "a")
    with open(test_dataset, "r") as file:
        for line in file:
            print("Calculating line:", index)
            true_positives = 0
            false_positives = 0
            false_negatives = 0
            f1_score = 0
            index += 1
            elements = line.split(";")
            article_id = elements[0]
            words_part = elements[2][2:-2]
            words_part = words_part.replace("\'", "").split("), (")
            article_words = []
            for entry in words_part:
                splitted = entry.split(",")
                article_words.append((splitted[0].strip(), splitted[1].strip()))
            categories_part = elements[3][1:-2]
            categories_part = categories_part.replace("\'", "")
            article_categories = [category.strip() for category in categories_part.split(",")]

            result = clasify_topic(article_words, article_id, num_results=len(article_categories))
            result = [tuple[0] for tuple in result]
            for category in result:
                if category in article_categories:
                    true_positives += 1
                else:
                    false_positives += 1
            false_negatives += sum([1 for category in article_categories if category not in result])
            true_positives_global += true_positives
            false_negatives_global += false_negatives
            false_positives_global += false_positives
            if (true_positives + false_positives) > 0:
                precision = true_positives / (true_positives + false_positives)
            if (true_positives + false_negatives) > 0:
                recall = true_positives / (true_positives + false_negatives)
            if (precision + recall) > 0:
                f1_score = 2 * (recall * precision) / (recall + precision)
            print(article_categories)
            print(str.format("Categories: {} | Precision: {} | Recall: {} | F1 Score: {}", len(article_categories),
                             precision, recall, f1_score))
            file_results.write(str.format("{}; {}; {}; {}; {}; {}; {}\n", article_id, len(article_categories)
                                          , precision, recall, f1_score, str(article_categories), str(result)))

    precision = true_positives_global / (true_positives_global + false_positives_global)
    recall = true_positives_global / (true_positives_global + false_negatives_global)
    f1_score = 2 * (recall * precision) / (recall + precision)
    print(str.format("Precision: {} | Recall: {} | F1 Score: {}", precision, recall, f1_score))


if __name__ == '__main__':
    start_time = time.time()
    test_system(config.get("test_dataset"))
    print("Execution time took %.3f seconds" % (time.time() - start_time))
