import json
import logging as log
import re
import time
from functools import cmp_to_key
from random import shuffle
from operator import itemgetter
from multiprocessing import Pool

import math

import os

with open('config.json') as json_data_file:
    config = json.load(json_data_file)
    config_pp = config.get("preprocess")
    if config.get("verbose", False):
        log.basicConfig(format="%(message)s", level=log.INFO)


def shuffle_dataset(file_path, file_path_output, file_path_temp):
    print("Transformación Schwartziana")
    num_lines = add_indexes(file_path, file_path_temp)
    print("División archivo en bloques")
    num_blocks = divide_in_blocks(file_path_temp, num_lines=num_lines)
    print("Ordenación de los bloques")
    sort_blocks(file_path_temp, num_blocks, processes=config_pp.get("threads", 4))
    print("k-way merge")
    k_way_merge(file_path_output, file_path_temp, num_blocks)


def add_indexes(file_path, file_path_temp):
    num_lines = sum(1 for line in open(file_path, "r"))
    indexes = list(range(num_lines))
    shuffle(indexes)
    lines = []
    index = 0
    output_file = open(file_path_temp + "_indexed", "w")
    with open(file_path, "r") as file:
        for line in file:
            lines.append(str(indexes[index]) + "#" + line)
            if len(lines) > 100000:
                output_file.writelines(lines)
                lines = []
                print("Wroted", str(index), "lines")
            index += 1
    output_file.writelines(lines)

    output_file.close()

    return num_lines


def divide_in_blocks(file_path_temp, block_size=100000, num_lines=0):
    if num_lines == 0:
        num_lines = sum(1 for line in open(file_path_temp + "_indexed", "r"))

    num_blocks = int(math.ceil(num_lines / block_size))

    index = 0
    dataset_file = open(file_path_temp + "_indexed", "r")
    for block in range(num_blocks):
        print(str.format("Writting block number {}", str(block)))
        block_file = open(file_path_temp + "_block_" + str(block), "w")
        lines = []
        for x in range(block_size):
            if index < num_lines:
                lines.append(dataset_file.readline())
                index += 1
        block_file.writelines(lines)
        block_file.close()

    dataset_file.close()

    return num_blocks


def sort_blocks(file_path_temp, num_blocks, processes=4):
    for block in range(num_blocks):
        print("Sorting block", str(block))
        sort_block(file_path_temp + "_block_" + str(block))


def sort_block(file_path):
    file = open(file_path, "r")
    lines = file.readlines()
    file.close()
    lines.sort(key=cmp_to_key(compare_lines))
    file = open(file_path, "w")
    file.writelines(lines)
    file.close()


def compare_lines(line_a, line_b):
    index_a = int(line_a.split("#")[0])
    index_b = int(line_b.split("#")[0])
    comparation = index_a - index_b
    if comparation < 0:
        result= -1
    elif comparation > 0:
        result = 1
    else:
        result = 0
    return result

def k_way_merge(file_path_output, file_path_temp, num_blocks, buffer=100000):
    files_dict = {}
    files_lines_dict = {}
    output_buffer = []
    output_file = open(file_path_output, "w")
    for block in range(num_blocks):
        block_file = open(file_path_temp + "_block_" + str(block), "r")
        files_dict[block] = block_file
        files_lines_dict[block] = block_file.readlines(100)

    done = False
    while not done:
        min_block = -1
        min_line = ""
        keys = files_lines_dict.keys()
        for key in keys:
            line = get_line(files_dict, files_lines_dict, key)
            if len(line):
                if min_block < 0 or compare_lines(line, min_line) < 0:
                    min_line = line
                    min_block = key
        if len(min_line):
            output_buffer.append(min_line.split("#")[1])
            pop_line(files_dict, files_lines_dict, min_block)
            if len(output_buffer) >= buffer:
                output_file.writelines(output_buffer)
                output_buffer = []
                print(str.format("Wtritten {} lines into {}", buffer, file_path_output))
        else:
            done = True

    output_file.writelines(output_buffer)
    output_file.close()


def get_line(files_dict, files_lines_dict, block):
    result = ""
    if block in files_lines_dict:
        lines = files_lines_dict.get(block, [])
        if len(lines):
            result = lines[0]
        else:
            file = files_dict.get(block)
            lines = file.readlines(100)
            files_lines_dict[block] = lines
            if len(lines):
                result = lines[0]
    return result


def pop_line(files_dict, files_lines_dict, block):
    line = get_line(files_dict, files_lines_dict, block)
    if len(line):
        files_lines_dict[block] = files_lines_dict[block][1:]

if __name__ == "__main__":
    start_time = time.time()
    shuffle_dataset(config_pp.get("dataset_shuffle_input_path", "./dataset"),
                    config_pp.get("dataset_shuffled_path", "./dataset"),
                    config_pp.get("dataset_shuffle_temp_path", "./dataset"))
    print("Execution time took %.3f seconds" % (time.time() - start_time))
