import os
from pathlib import Path
import inspect
import json
import csv

class EmptyDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.allowed_keys = kwargs.keys()

    def __setitem__(self, key, value):
        if key not in self.allowed_keys:
            raise KeyError('The key {} is not allowed'.format(key))
        else:
            super().__setitem__(key, value)

class FullDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        if key not in self:
            raise KeyError('The key {} is not allowed'.format(key))
        else:
            super().__setitem__(key, value)

word_pattern = {
    "word": "",
    "jyutping": "",
    "jyutping_mode": 0,
    "details": []
}

detail_pattern = {
    "source": "",
    "freq": "",
    "POS": "",
    "explanation_Chinese": "",
    "explanation_English": "",
    "example_Chinese": "",
    "example_English": "",
    "words_with_similar_meaning": "",
    "words_with_similar_jyutping":"",
    "remark":"",
    "#strokes": 0
}

def data_merge(main_dict, word_dict, detail_dict):
    word_jyutping = word_dict["word"] + word_dict["jyutping"]
    if word_jyutping in main_dict:
        main_dict[word_jyutping]["details"].append(detail_dict)
    else:
        word_dict["details"] = [detail_dict]
        main_dict[word_jyutping] = word_dict


def canclid(file_path):
    data = dict()
    data_source_id = file_name_des = inspect.stack()[0][3] +"_"+ file_path.split(os.sep)[-1]
    # create output directory
    output_dir = Path.joinpath(Path(os.path.dirname(os.path.realpath(__file__))), "preprocessed", inspect.stack()[0][3])
    output_file_name = Path.joinpath(output_dir, file_name_des+".json")
    os.makedirs(output_dir, exist_ok=True)
    # file analysis
    file_name_src = file_path.split(os.sep)[-1]
    if file_path.endswith(".yaml") or file_path.endswith(".tsv"):
        remove_percent_sign = False
        remove_last_column = False
        extract_third_column_as_jyutping = False
        if file_name_src == "jp_table_char_dict.yaml":
            remove_last_column = True
            start_position = 12
        elif file_name_src == "alt_dict_lettered_yale.dict.yaml":
            start_position = 32
        elif file_name_src == "alt_dict_yale.dict.yaml":
            remove_percent_sign = True
            start_position = 46
        elif file_name_src == "jp_table_ordered.tsv":
            start_position = 2
            extract_third_column_as_jyutping = True
        with open(file_path) as f: 
            count = 0
            for line in f:
                count += 1
                if count < start_position:
                    continue
                l = line.strip()
                if l == "": 
                    continue
                if l.startswith("#"):
                    continue
                items = l.split(" ")
                items = [item.strip() for item in items]
                # prepare the word instance
                word_dict = EmptyDict(word_pattern)
                word_dict["word"] = items[0]
                jyutping = " ".join(items[1:])
                if remove_last_column:
                    jyutping = " ".join(items[1:-1])
                if remove_percent_sign:
                    if items[-1].endswith("%"):
                        jyutping = " ".join(items[1:-1])
                if extract_third_column_as_jyutping:
                    jyutping = items[2]
                word_dict["jyutping"] = jyutping
                word_dict["jyutping_mode"] = 6
                # prepare the detail instance
                detail_dict = EmptyDict(detail_pattern)
                detail_dict["source"] = data_source_id
                # merge data
                data_merge(data, word_dict, detail_dict)
    elif file_path.endswith(".csv"):
        if file_name_src == "can_orth_association.csv":
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word_dict = EmptyDict(word_pattern)
                    word_dict["word"] = row["粵字"].strip()
                    word_dict["jyutping"] = row["粵拼"].strip()
                    word_dict["jyutping_mode"] = 6
                    detail_dict = EmptyDict(detail_pattern)
                    detail_dict["source"] = data_source_id
                    word_with_same_jyutping = row["同音字"].strip()
                    if word_with_same_jyutping != "/": 
                        detail_dict["words_with_similar_jyutping"] = word_with_same_jyutping
                    detail_dict["example_Chinese"] = row["簡略解釋與例子"].strip()
        elif file_name_src == "can_orth_draft.csv":
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word_dict = EmptyDict(word_pattern)
                    word_dict["word"] = row["粵研社（粵語協會）"].strip()
                    word_dict["jyutping"] = row["粵拼"].strip()
                    word_dict["jyutping_mode"] = 6
                    detail_dict = EmptyDict(detail_pattern)
                    detail_dict["source"] = data_source_id
                    detail_dict["example_Chinese"] = row["意思及例子"].strip()
        elif file_name_src == "can_orth_houxingquan.csv":
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word_dict = EmptyDict(word_pattern)
                    word_dict["word"] = row["推荐字"].strip()
                    word_dict["jyutping"] = row["字音（粤拼）"].strip()
                    word_dict["jyutping_mode"] = 6
                    detail_dict = EmptyDict(detail_pattern)
                    detail_dict["source"] = data_source_id
                    detail_dict["words_with_similar_meaning"] = row["异体字"].strip()
                    detail_dict["words_with_similar_jyutping"] = row["同/近音字 (潜在异体字）"].strip()
                    detail_dict["explanation_Chinese"] = row["字（词）义"].strip()
        elif file_name_src == "can_orth_main.csv":
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word_dict = EmptyDict(word_pattern)
                    word_dict["word"] = row["通用粵字"].strip()
                    word_dict["jyutping"] = row["學會粵拼"].strip()
                    word_dict["jyutping_mode"] = 6
                    detail_dict = EmptyDict(detail_pattern)
                    detail_dict["source"] = data_source_id
                    detail_dict["example_Chinese"] = row["意思及例子"].strip()
                    detail_dict["remark"] = row["疑問或建議/註解"].strip()
        elif file_name_src == "can_orth_research_group.csv":
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word_dict = EmptyDict(word_pattern)
                    word_dict["word"] = row["通用粵字"].strip()
                    word_dict["jyutping"] = row["學會粵拼"].strip()
                    word_dict["jyutping_mode"] = 6
                    detail_dict = EmptyDict(detail_pattern)
                    detail_dict["source"] = data_source_id
                    detail_dict["example_Chinese"] = row["意思及例子"].strip()
                    detail_dict["remark"] = row["疑問或建議/註解"].strip()
    # write the data into a json file
    with open(output_file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def cifu(file_path):
    pass

def hanyu(file_path):
    pass

def hkcancor(file_path):
    pass

def hkcc(file_path):
    return
    data = dict()
    data_source_id = folder_name = file_name = inspect.stack()[0][3]
    # localize and generate the output directory
    output_dir = Path.joinpath(Path(os.path.dirname(os.path.realpath(__file__))), "preprocessed", folder_name)
    output_file_name = Path.joinpath(Path(os.path.dirname(os.path.realpath(__file__))), "preprocessed", folder_name, file_name+".json")
    os.makedirs(output_dir, exist_ok=True)
    # load the source data
    json_file_path = os.path.join(dir_source, folder_name, file_name+'.json')
    data_source = json.load(open(json_file_path, 'r'))
    # transform the format
    for sentence in data_source:
        word_jyutping_added = []
        words = sentence["words"]
        jyutpings = sentence["jyutping"]
        for i, jyutping in enumerate(jyutpings.split()):
            if jyutping == "*": 
                continue
            word = words[i]
            word_jyutping = word+jyutping
            if word_jyutping in word_jyutping_added:
                continue
            word_jyutping_added.append(word_jyutping)
            # prepare the word instance
            word_dict = EmptyDict(word_pattern)
            word_dict["word"] = word
            word_dict["jyutping"] = jyutping
            word_dict["jyutping_mode"] = 6
            # prepare the detail instance
            detail_dict = EmptyDict(detail_pattern)
            detail_dict["source"] = data_source_id
            detail_dict["example_Chinese"] = words
            # merge data
            data_merge(data, word_dict, detail_dict)
    
    # write the data into a json file
    with open(output_file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def lexi_mf(file_path):
    pass

def loanword(file_path):
    pass

def SpeechOcean(file_path):
    pass

def TonyDictionary(file_path):
    pass

def words_faiman(file_path):
    pass

def words_zidin(file_path):
    pass

if __name__ == "__main__":
    dir_source = "/home/tristanwu/TRS/MyWebCrawler/raw"
    # dir_preprocessed = "/home/tristanwu/TRS/MyWebCrawler/preprocessed"
    file_cnt = 0
    for subdir, dirs, files in os.walk(dir_source):
        for file in files:
            #print os.path.join(subdir, file)
            filepath = subdir + os.sep + file
            dir_name = subdir.split(os.sep)[-1]
            eval(dir_name)(filepath)
