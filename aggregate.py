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

if __name__ == "__main__":
    dir_source = "/home/tristanwu/TRS/MyWebCrawler/preprocessed"
    # dir_preprocessed = "/home/tristanwu/TRS/MyWebCrawler/preprocessed"
    output_file_path = "/home/tristanwu/TRS/MyWebCrawler/output/result.csv"
    file_cnt = 0
    index = 1
    for subdir, dirs, files in os.walk(dir_source):
        for file in files:
            #print os.path.join(subdir, file)
            filepath = subdir + os.sep + file
            dir_name = subdir.split(os.sep)[-1]
            data_source = json.load(open(filepath, 'r'))
            with open(output_file_path, 'w', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=column_titles)
                writer.writeheader()
                for word in data_source.values():
                    writer.writerows(prepare_csv_line(word, index))
                    index += 1

