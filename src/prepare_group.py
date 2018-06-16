import json
import logging as log
import time

import math

with open('config.json') as json_data_file:
    config = json.load(json_data_file)
    config_pp = config.get("preprocess")
    if config.get("verbose", False):
        log.basicConfig(format="%(message)s", level=log.INFO)


def create_group(input_path, output_path, num_blocks, block, num_lines=0):
    if not num_lines:
        num_lines = sum(1 for line in open(input_path, "r"))
    block_size = math.ceil(num_lines / num_blocks)

    first_test = block_size * block
    last_test = min((block + 1) * block_size, num_lines)

    test_file = open(output_path + "test_" + str(block), "w")
    train_file = open(output_path + "train_" + str(block), "w")
    lines_test = []
    lines_train = []

    max_items = 100000

    index = 0

    log.info("Writting files")

    with open(input_path, "r") as file:
        for line in file:
            if first_test <= index < last_test:
                lines_test.append(line)
            else:
                lines_train.append(line)

            if len(lines_test) > max_items:
                test_file.writelines(lines_test)
                lines_test = []
            if len(lines_train) > max_items:
                train_file.writelines(lines_train)
                lines_train = []
            index += 1

    test_file.writelines(lines_test)
    train_file.writelines(lines_train)

    log.info("Closing files")
    test_file.close()
    train_file.close()
    log.info("Files closed")


if __name__ == "__main__":
    start_time = time.time()
    print("Building cv datasets")
    create_group(config_pp.get("dataset_shuffled_path"), config_pp.get("cross_validation_path"), 800, 0)
    print("Execution time took %.3f seconds" % (time.time() - start_time))
