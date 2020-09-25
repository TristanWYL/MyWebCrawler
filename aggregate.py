import os
import json
from preprocess import *
import csv


column_titles = ["index"] + [key for key in word_pattern.keys() if key!="details"] + [key for key in detail_pattern.keys()]

def prepare_csv_line(word, index):
    rows = []
    for detail in word["details"]:
        w = {k:v for k,v in word.items() if k!="details"}
        rows.append({**w, **detail, "index":index})
    return rows

def data_merge(main_dict, word_dict):
    word_jyutping = word_dict["word"] + word_dict["jyutping"]
    if word_jyutping in main_dict:
        for details in word_dict["details"]:
            main_dict[word_jyutping]["details"].append(details)
    else:
        main_dict[word_jyutping] = word_dict

if __name__ == "__main__":
    data = dict()
    dir_source = "/home/tristanwu/TRS/MyWebCrawler/preprocessed"
    # dir_preprocessed = "/home/tristanwu/TRS/MyWebCrawler/preprocessed"
    output_file_path = "/home/tristanwu/TRS/MyWebCrawler/output/result.csv"
    file_cnt = 0
    index = 1

    # Save the data
    # for subdir, dirs, files in os.walk(dir_source):
    #     for file in files:
    #         #print os.path.join(subdir, file)
    #         filepath = subdir + os.sep + file
    #         dir_name = subdir.split(os.sep)[-1]
    #         # aggregating the data into the "data" dict
    #         data_source = json.load(open(filepath, 'r'))
    #         for _, word in data_source.items():
    #             data_merge(data, word)
    # # save the data as the csv file
    # with open(output_file_path, 'w', encoding='utf-8') as f:
    #     writer = csv.DictWriter(f, fieldnames=column_titles)
    #     writer.writeheader()
    #     for word in data.values():
    #         writer.writerows(prepare_csv_line(word, index))
    #         index += 1

    # statistics
    data_source_cnt = 0
    for subdir, dirs, files in os.walk(dir_source):
        for file in files:
            data_source_cnt += 1
            #print os.path.join(subdir, file)
            filepath = subdir + os.sep + file
            dir_name = subdir.split(os.sep)[-1]
            # aggregating the data into the "data" dict
            data_source = json.load(open(filepath, 'r'))
            for _, word in data_source.items():
                data_merge(data, word)
    # save the data as the csv file
    with open(output_file_path, 'w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=column_titles)
        writer.writeheader()
        for word in data.values():
            writer.writerows(prepare_csv_line(word, index))
            index += 1

