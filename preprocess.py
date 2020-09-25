import os
from pathlib import Path
import inspect
import json
import csv
import xml.etree.ElementTree as ET
import re

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

def data_merge_for_single_file(main_dict, word_dict, detail_dict):
    word_jyutping = word_dict["word"] + word_dict["jyutping"]
    if word_jyutping in main_dict:
        # remove duplications
        for details in main_dict[word_jyutping]["details"]:
            same_detail = True
            for k, v in details.items():
                if k not in detail_dict:
                    same_detail = False
                    break
                if detail_dict[k] != v:
                    same_detail = False
                    break
            if same_detail:
                return
        main_dict[word_jyutping]["details"].append(detail_dict)
    else:
        word_dict["details"] = [detail_dict]
        main_dict[word_jyutping] = word_dict


def canclid(file_path):
    return
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
        start_position = 1
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
                items = l.split()
                items = [item.strip() for item in items]
                # prepare the word instance
                word_dict = EmptyDict(**word_pattern)
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
                detail_dict = EmptyDict(**detail_pattern)
                detail_dict["source"] = data_source_id
                # merge data
                data_merge_for_single_file(data, word_dict, detail_dict)
    elif file_path.endswith(".csv"):
        if file_name_src == "can_orth_association.csv":
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word_dict = EmptyDict(**word_pattern)
                    word_dict["word"] = row["粵字"].strip()
                    word_dict["jyutping"] = row["粵拼"].strip()
                    word_dict["jyutping_mode"] = 6
                    detail_dict = EmptyDict(**detail_pattern)
                    detail_dict["source"] = data_source_id
                    word_with_same_jyutping = row["同音字"].strip()
                    if word_with_same_jyutping != "/": 
                        detail_dict["words_with_similar_jyutping"] = word_with_same_jyutping
                    detail_dict["example_Chinese"] = row["簡略解釋與例子"].strip()
                    data_merge_for_single_file(data, word_dict, detail_dict)
        elif file_name_src == "can_orth_draft.csv":
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word_dict = EmptyDict(**word_pattern)
                    word_dict["word"] = row["粵研社（粵語協會）"].strip()
                    word_dict["jyutping"] = row["粵拼"].strip()
                    word_dict["jyutping_mode"] = 6
                    detail_dict = EmptyDict(**detail_pattern)
                    detail_dict["source"] = data_source_id
                    detail_dict["example_Chinese"] = row["意思及例子"].strip()
                    data_merge_for_single_file(data, word_dict, detail_dict)
        elif file_name_src == "can_orth_houxingquan.csv":
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word_dict = EmptyDict(**word_pattern)
                    word_dict["word"] = row["推荐字"].strip()
                    word_dict["jyutping"] = row["\ufeff字音（粤拼）"].strip()
                    word_dict["jyutping_mode"] = 6
                    detail_dict = EmptyDict(**detail_pattern)
                    detail_dict["source"] = data_source_id
                    detail_dict["words_with_similar_meaning"] = row["异体字"].strip()
                    detail_dict["words_with_similar_jyutping"] = row["同/近音字 (潜在异体字）"].strip()
                    detail_dict["explanation_Chinese"] = row["字（词）义"].strip()
                    data_merge_for_single_file(data, word_dict, detail_dict)
        elif file_name_src == "can_orth_main.csv":
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word_dict = EmptyDict(**word_pattern)
                    word_dict["word"] = row["通用粵字"].strip()
                    word_dict["jyutping"] = row["學會粵拼"].strip()
                    word_dict["jyutping_mode"] = 6
                    detail_dict = EmptyDict(**detail_pattern)
                    detail_dict["source"] = data_source_id
                    detail_dict["example_Chinese"] = row["意思及例子"].strip()
                    detail_dict["remark"] = row["疑問或建議/註解"].strip()
                    data_merge_for_single_file(data, word_dict, detail_dict)
        elif file_name_src == "can_orth_research_group.csv":
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word_dict = EmptyDict(**word_pattern)
                    word_dict["word"] = row["通用粵字"].strip()
                    word_dict["jyutping"] = row["學會粵拼"].strip()
                    word_dict["jyutping_mode"] = 6
                    detail_dict = EmptyDict(**detail_pattern)
                    detail_dict["source"] = data_source_id
                    detail_dict["example_Chinese"] = row["意思及例子"].strip()
                    detail_dict["remark"] = row["疑問或建議/註解"].strip()
                    data_merge_for_single_file(data, word_dict, detail_dict)
        elif file_name_src == "can_orth_yueyinxiaojing_general.csv":
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word_dict = EmptyDict(**word_pattern)
                    word_dict["word"] = row["字頭"].strip()
                    word_dict["jyutping"] = row["粵-聲韻調"].strip()
                    word_dict["jyutping_mode"] = '6*'
                    detail_dict = EmptyDict(**detail_pattern)
                    detail_dict["source"] = data_source_id
                    detail_dict["remark"] = row["釋義補充"].strip()
                    detail_dict["explanation_Chinese"] = row["廣韻釋義"].strip()
                    data_merge_for_single_file(data, word_dict, detail_dict)
        elif file_name_src == "can_orth_yueyinxiaojing_words_with_same_jyutping.csv":
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    words_with_same_reading = row["粵-同音字"].strip()
                    for w in words_with_same_reading:
                        word_dict = EmptyDict(**word_pattern)
                        word_dict["word"] = w
                        word_dict["jyutping"] = row["粵-聲韻調"].strip()
                        word_dict["jyutping_mode"] = '6*'
                        detail_dict = EmptyDict(**detail_pattern)
                        detail_dict["source"] = data_source_id
                        detail_dict["words_with_similar_jyutping"] = words_with_same_reading.replace(w, "")
                        data_merge_for_single_file(data, word_dict, detail_dict)
        elif file_name_src == "can_orth_yueyinxiaojing.csv":
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    words_with_same_reading = row["粵京對應"].strip()
                    for w in words_with_same_reading:
                        word_dict = EmptyDict(**word_pattern)
                        word_dict["word"] = w
                        word_dict["jyutping"] = row["粵-聲韻調"].strip()
                        word_dict["jyutping_mode"] = '6*'
                        detail_dict = EmptyDict(**detail_pattern)
                        detail_dict["source"] = data_source_id
                        detail_dict["words_with_similar_jyutping"] = words_with_same_reading.replace(w, "")
                        data_merge_for_single_file(data, word_dict, detail_dict)
    # write the data into a json file
    with open(output_file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def cifu(file_path):
    pass

def hanyu(file_path):
    pass

def hkcancor(file_path):
    return
    data = dict()
    data_source_id = file_name_des = inspect.stack()[0][3] +"_"+ file_path.split(os.sep)[-1]
    # create output directory
    output_dir = Path.joinpath(Path(os.path.dirname(os.path.realpath(__file__))), "preprocessed", inspect.stack()[0][3])
    output_file_name = Path.joinpath(output_dir, file_name_des+".json")
    os.makedirs(output_dir, exist_ok=True)
    # file analysis
    file_name_src = file_path.split(os.sep)[-1]

    # split the jyutpings
    pattern_for_jyutping = r"[a-zA-Z]+\d"

    # wrap the xml file due to multiple root nodes
    f = Path(file_path)
    f_xml = b'<content>' + f.read_bytes() + b'</content>'
    
    tree = ET.fromstring(f_xml)
    tags = tree.findall('sent/sent_tag')
    unwanted_words = "?。，-？、！"
    for tag in tags:
        lines = tag.text.split()
        for line in lines:
            items = line.split('/')
            if len(items) < 3: continue
            if items[0][0] in unwanted_words:
                continue
            # prepare the word instance
            word_dict = EmptyDict(**word_pattern)
            word_dict["word"] = items[0]

            jyutpings = re.findall(pattern_for_jyutping, items[2])
            word_dict["jyutping"] = " ".join(jyutpings)
            word_dict["jyutping_mode"] = 6
            # prepare the detail instance
            detail_dict = EmptyDict(**detail_pattern)
            detail_dict["source"] = data_source_id
            detail_dict["POS"] = items[1]
            # merge data
            data_merge_for_single_file(data, word_dict, detail_dict)
    
    # write the data into a json file
    with open(output_file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

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
            word_dict = EmptyDict(**word_pattern)
            word_dict["word"] = word
            word_dict["jyutping"] = jyutping
            word_dict["jyutping_mode"] = 6
            # prepare the detail instance
            detail_dict = EmptyDict(**detail_pattern)
            detail_dict["source"] = data_source_id
            detail_dict["example_Chinese"] = words
            # merge data
            data_merge_for_single_file(data, word_dict, detail_dict)
    
    # write the data into a json file
    with open(output_file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def lexi_mf(file_path):
    return
    data = dict()
    data_source_id = file_name_des = inspect.stack()[0][3] +"_"+ file_path.split(os.sep)[-1]
    # create output directory
    output_dir = Path.joinpath(Path(os.path.dirname(os.path.realpath(__file__))), "preprocessed", inspect.stack()[0][3])
    output_file_name = Path.joinpath(output_dir, inspect.stack()[0][3]+".json")
    os.makedirs(output_dir, exist_ok=True)
    # file analysis
    file_name_src = file_path.split(os.sep)[-1]
    data_source = json.load(open(file_path, 'r'))
    for word in data_source:
        for info in word['info']:
            word_dict = EmptyDict(**word_pattern)
            word_dict["word"] = word["word"]
            word_dict["jyutping"] = info["jyutping"]
            word_dict["jyutping_mode"] = 6
            # prepare the detail instance
            detail_dict = EmptyDict(**detail_pattern)
            detail_dict["source"] = inspect.stack()[0][3]
            detail_dict["explanation_Chinese"] = info["note"]
            detail_dict["example_Chinese"] = info["examples"]
            # merge data
            data_merge_for_single_file(data, word_dict, detail_dict)
    
    # write the data into a json file
    with open(output_file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def loanword(file_path):
    return
    data = dict()
    data_source_id = file_name_des = inspect.stack()[0][3] +"_"+ file_path.split(os.sep)[-1]
    # create output directory
    output_dir = Path.joinpath(Path(os.path.dirname(os.path.realpath(__file__))), "preprocessed", inspect.stack()[0][3])
    output_file_name = Path.joinpath(output_dir, inspect.stack()[0][3]+".json")
    os.makedirs(output_dir, exist_ok=True)
    # file analysis
    file_name_src = file_path.split(os.sep)[-1]
    data_source = json.load(open(file_path, 'r'))
    for word in data_source:
        for info in word['wordprop']:
            word_dict = EmptyDict(**word_pattern)
            word_dict["word"] = word["chars"]
            word_dict["jyutping"] = word["hw"]
            word_dict["jyutping_mode"] = 6
            # prepare the detail instance
            detail_dict = EmptyDict(**detail_pattern)
            detail_dict["source"] = inspect.stack()[0][3]
            detail_dict["POS"] = info["ps"]
            detail_dict["explanation_Chinese"] = info["stch"]
            detail_dict["example_Chinese"] = info["exchar"]
            detail_dict["explanation_English"] = info["df"]
            detail_dict["example_English"] = info["exeng"]
            # merge data
            data_merge_for_single_file(data, word_dict, detail_dict)
    
    # write the data into a json file
    with open(output_file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def SpeechOcean(file_path):
    return
    data = dict()
    data_source_id = file_name_des = inspect.stack()[0][3] +"_"+ file_path.split(os.sep)[-1]
    # create output directory
    output_dir = Path.joinpath(Path(os.path.dirname(os.path.realpath(__file__))), "preprocessed", inspect.stack()[0][3])
    output_file_name = Path.joinpath(output_dir, inspect.stack()[0][3]+".json")
    os.makedirs(output_dir, exist_ok=True)
    # file analysis
    file_name_src = file_path.split(os.sep)[-1]
    with open(file_path) as f: 
            count = 0
            for line in f:
                count += 1
                if count < 2:
                    continue
                items = line.split('\t')
                word_dict = EmptyDict(**word_pattern)
                word_dict["word"] = items[0].strip()
                word_dict["jyutping"] = items[1].strip()
                word_dict["jyutping_mode"] = 6
                # prepare the detail instance
                detail_dict = EmptyDict(**detail_pattern)
                detail_dict["source"] = inspect.stack()[0][3]
                # merge data
                data_merge_for_single_file(data, word_dict, detail_dict)
    
    # write the data into a json file
    with open(output_file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def TonyDictionary(file_path):
    return
    data = dict()
    data_source_id = file_name_des = inspect.stack()[0][3] +"_"+ file_path.split(os.sep)[-1]
    # create output directory
    output_dir = Path.joinpath(Path(os.path.dirname(os.path.realpath(__file__))), "preprocessed", inspect.stack()[0][3])
    output_file_name = Path.joinpath(output_dir, file_name_des+".json")
    os.makedirs(output_dir, exist_ok=True)
    # file analysis
    file_name_src = file_path.split(os.sep)[-1]

    first_line = 1
    last_line = -1
    
    if file_name_src.startswith("char"):
        cur_continuum = 0
        valid_continuum = [(74,3654),(4065,9463),(9829,-1)]
        with open(file_path) as f: 
            count = 0
            start, end = valid_continuum[cur_continuum]
            for line in f:
                count += 1
                if count<start:
                    continue
                if end != -1 and count >= end:
                    cur_continuum += 1
                    if cur_continuum >= len(valid_continuum):
                        break
                    start, end = valid_continuum[cur_continuum]
                    continue
                if "unknown" in line:
                    continue
                items = line.split(',')
                word_dict = EmptyDict(**word_pattern)
                word_dict["word"] = items[0].strip()
                word_dict["jyutping"] = items[1].strip()
                word_dict["jyutping_mode"] = 6
                # prepare the detail instance
                detail_dict = EmptyDict(**detail_pattern)
                detail_dict["source"] = data_source_id
                # merge data
                data_merge_for_single_file(data, word_dict, detail_dict)
    elif file_name_src.startswith("main"):
        last_line = 59535
        with open(file_path) as f: 
            count = 0
            for line in f:
                count += 1
                if count < first_line:
                    continue
                items = line.split(',')
                word_dict = EmptyDict(**word_pattern)
                word_dict["word"] = items[0].strip()
                word_dict["jyutping"] = items[1].strip().replace('-', ' ')
                word_dict["jyutping_mode"] = 6
                # prepare the detail instance
                detail_dict = EmptyDict(**detail_pattern)
                detail_dict["source"] = data_source_id
                # merge data
                data_merge_for_single_file(data, word_dict, detail_dict)
    elif file_name_src.startswith("user"):
        with open(file_path) as f: 
            for line in f:
                items = line.split(',')
                word_dict = EmptyDict(**word_pattern)
                word_dict["word"] = items[0].strip()
                word_dict["jyutping"] = items[1].strip().replace('-', ' ')
                word_dict["jyutping_mode"] = 6
                # prepare the detail instance
                detail_dict = EmptyDict(**detail_pattern)
                detail_dict["source"] = data_source_id
                # merge data
                data_merge_for_single_file(data, word_dict, detail_dict)
    # write the data into a json file
    with open(output_file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
def words_faiman(file_path):
    return
    data = dict()
    data_source_id = file_name_des = inspect.stack()[0][3] +"_"+ file_path.split(os.sep)[-1].split('.')[-2]
    # create output directory
    output_dir = Path.joinpath(Path(os.path.dirname(os.path.realpath(__file__))), "preprocessed", inspect.stack()[0][3])
    output_file_name = Path.joinpath(output_dir, file_name_des+".json")
    os.makedirs(output_dir, exist_ok=True)
    # file analysis
    file_name_src = file_path.split(os.sep)[-1]

    if file_path.endswith(".csv"):
        return
    # load the source data
    data_source = json.load(open(file_path, 'r'))
    if file_path.endswith("charlist.json"):
        for word, jyutpings in data_source.items():
            for jyutping, _ in jyutpings.items():
                word_dict = EmptyDict(**word_pattern)
                word_dict["word"] = word.strip()
                word_dict["jyutping"] = jyutping.strip()
                word_dict["jyutping_mode"] = 6
                # prepare the detail instance
                detail_dict = EmptyDict(**detail_pattern)
                detail_dict["source"] = data_source_id
                # merge data
                data_merge_for_single_file(data, word_dict, detail_dict)
    elif file_path.endswith("wordslist.json"):
        for word, jyutpings in data_source.items():
            if word == "":
                continue
            for jyutping in jyutpings:
                word_dict = EmptyDict(**word_pattern)
                word_dict["word"] = word.strip()
                word_dict["jyutping"] = jyutping.strip()
                word_dict["jyutping_mode"] = 6
                # prepare the detail instance
                detail_dict = EmptyDict(**detail_pattern)
                detail_dict["source"] = data_source_id
                # merge data
                data_merge_for_single_file(data, word_dict, detail_dict)
    # write the data into a json file
    with open(output_file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def words_zidin(file_path):
    data = dict()
    data_source_id = file_name_des = inspect.stack()[0][3] +"_"+ file_path.split(os.sep)[-1]
    # create output directory
    output_dir = Path.joinpath(Path(os.path.dirname(os.path.realpath(__file__))), "preprocessed", inspect.stack()[0][3])
    output_file_name = Path.joinpath(output_dir, inspect.stack()[0][3]+".json")
    os.makedirs(output_dir, exist_ok=True)
    # file analysis
    file_name_src = file_path.split(os.sep)[-1]
    data_source = json.load(open(file_path, 'r'))
    for item in data_source:
        for info in item['info']:
            word_dict = EmptyDict(**word_pattern)
            word_dict["word"] = item["word"]
            i = 0
            jyutping = ""
            for jp in info["jyutping"]:
                if i % 2 == 0:
                    jyutping += jp
                else:
                    jyutping += jp+" "
                i += 1
            word_dict["jyutping"] = jyutping.strip()
            word_dict["jyutping_mode"] = 6
            # prepare the detail instance
            detail_dict = EmptyDict(**detail_pattern)
            detail_dict["source"] = inspect.stack()[0][3]
            detail_dict["POS"] = info["pos"]
            detail_dict["explanation_Chinese"] = info["explain"]["Chinese"]
            detail_dict["explanation_English"] = info["explain"]["English"]
            example_Chinese_list = []
            example_English_list = []
            for example in info["examples"]:
                example_Chinese_list.append(example["Chinese"] if "Chinese" in example else "")
                example_English_list.append(example["English"] if "English" in example else "")
            for phrase in info["phrases"]:
                example_Chinese_list.append(phrase["Chinese"] if "Chinese" in phrase else "")
                example_English_list.append(phrase["English"] if "English" in phrase else "")
            detail_dict["example_Chinese"] = example_Chinese_list
            detail_dict["example_English"] = example_English_list
            # merge data
            data_merge_for_single_file(data, word_dict, detail_dict)

    for item in data_source:
        for info in item['info']:
            for phrase in info["phrases"]:
                if "Chinese" not in phrase:
                    continue
                txt = phrase["Chinese"]
                txt_list = re.split("\(|\)", txt)
                if len(txt_list) < 3:
                    continue
                word_dict = EmptyDict(**word_pattern)
                word_dict["word"] = txt_list[0]
                word_dict["jyutping"] = txt_list[1]
                word_dict["jyutping_mode"] = 6
                # prepare the detail instance
                detail_dict = EmptyDict(**detail_pattern)
                detail_dict["source"] = inspect.stack()[0][3]+"_phrase"
                detail_dict["explanation_English"] = phrase["English"] if "English" in phrase else ""
                # merge data
                data_merge_for_single_file(data, word_dict, detail_dict)

    # write the data into a json file
    with open(output_file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

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
