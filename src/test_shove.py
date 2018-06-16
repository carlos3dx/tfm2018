import json
import logging as log
# engine = create_engine('sqlite:///foo.db')
# test = Shove("sqlite:////test.db")
# test = Shove('lite://test.db', sync=10)
# test["a"] = 1
# test.sync()
# test["a"*10] = 2
# test["a"*1000] = 3
# test["a"*100000] = 5
# test.sync()
# print(test.get("a", 0))
# print(test.get("a"*10, 0))
# print(test.get("a"*1000, 0))
# print(test.get("a"*100000, 0))

with open('config.json') as json_data_file:
    config = json.load(json_data_file)
    config_shove = config.get("shove")
    config_db = config.get("wiki_db")
    config_categories = config.get("categories")
    shove_buffer = config_shove.get("buffer", 10)
    shove_folder = config_shove.get("folder_path", "./")
    # dataset = "/home/carlos3dx/Extra/tfm/dataset_clean_shuffled"
    # dataset = "/home/carlos3dx/Extra/tfm/dataset_clean"
    dataset= "../data/lda_results/topics_results_chicago10000_10.json"
    # dataset = config.get("train_dataset")
    if config.get("verbose", False):
        log.basicConfig(format="%(message)s", level=log.INFO)

# with open(dataset, "r") as data:
#     dictionary = json.load(data)
#
# num_topics = len(dictionary)
#
# for i in range(num_topics):
#     words = [x[0] for x in dictionary.get("topic_"+str(i))]
#
#     print(str.format("{} & {} \\\\\n\\hline", str(i), str.join(", ", words)))

file = open("/media/cvillarl/barracuda_4tb/train_100_slim", "w")
lines=[]
with open("/media/cvillarl/barracuda_4tb/train_100", "r") as data:
    for line in data:
        parts = line.split(";")
        lines.append(str.join(";", [parts[0], parts[1], "", parts[3]]))
        if len(lines) >= 1000000:
            file.writelines(lines)
            lines=[]
file.writelines(lines)
file.close()



