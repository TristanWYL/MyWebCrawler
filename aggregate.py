# %%
import os
import json
from preprocess import *
import csv
from pyecharts.charts import Bar
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts
import numpy as np

# %%
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

# %%
data = dict()
dir_source = "/home/tristanwu/TRS/MyWebCrawler/preprocessed"
# dir_preprocessed = "/home/tristanwu/TRS/MyWebCrawler/preprocessed"
output_file_dir = "/home/tristanwu/TRS/MyWebCrawler/output"
output_file_path = output_file_dir + "/result.csv"
file_cnt = 0
index = 1

# Save the data
for subdir, dirs, files in os.walk(dir_source):
    for file in files:
        #print os.path.join(subdir, file)
        filepath = subdir + os.sep + file
        dir_name = subdir.split(os.sep)[-1]
        # aggregating the data into the "data" dict
        data_source = json.load(open(filepath, 'r'))
        for _, word in data_source.items():
            data_merge(data, word)
# # save the data as the csv file
# with open(output_file_path, 'w', encoding='utf-8') as f:
#     writer = csv.DictWriter(f, fieldnames=column_titles)
#     writer.writeheader()
#     for word in data.values():
#         writer.writerows(prepare_csv_line(word, index))
#         index += 1

# %%
# statistics
IDEOGRAPHIC_SPACE = 0x3000
def is_asian(char):
    """Is the character Asian?"""

    # 0x3000 is ideographic space (i.e. double-byte space)
    # Anything over is an Asian character
    return ord(char) > IDEOGRAPHIC_SPACE

def len_of_asian_word(word):
    return sum([is_asian(c) for c in word])

# %%
data_source_word_cnt = {}
all_cnt = 0
rows = []
index = 0
for subdir, dirs, files in os.walk(dir_source):
    for file in files:
        filepath = subdir + os.sep + file
        with open(filepath, 'r') as f:
            data_source = json.load(f)
            row = []
            cnts = [0]*6
            index += 1
            row.append(index)
            row.append(data_source[list(data_source)[0]]["details"][0]["source"])
            for _, value in data_source.items():
                cnt_of_chinese_char = len_of_asian_word(value["word"])
                idx = cnt_of_chinese_char-1 if cnt_of_chinese_char<=5 else 4
                if idx == -1:
                    continue
                cnts[idx] += 1
            cnts[-1] = len(data_source)
            row.extend(cnts)
            rows.append(row)

# %% TOTAL
numbers = np.array(rows)
total = numbers[:,2:].astype(np.int).sum(axis=0).astype(int)
row = ["TOTAL", "-"]
row.extend(total)
rows.append(row)

# %% TOTAL UNIQUE
cnts = [0]*6
for _, value in data.items():
    cnt_of_chinese_char = len_of_asian_word(value["word"])
    idx = cnt_of_chinese_char-1 if cnt_of_chinese_char<=5 else 4
    if idx == -1:
        continue
    cnts[idx] += 1
cnts[-1] = len(data)
row = ["UNIQUE TOTAL","-"]
row.extend(cnts)
rows.append(row)

# %%
table = Table()
headers = ["Index", "Source", "#word_with_one_char",
"#word_with_two_char", 
"#word_with_three_char", 
"#word_with_four_char", 
"#word_with_five_plus_char", 
"#word"]
# rows = [
#     ["Brisbane", 5905, 1857594, 1146.4],
#     ["Adelaide", 1295, 1158259, 600.5],
#     ["Darwin", 112, 120900, 1714.7],
#     ["Hobart", 1357, 205556, 619.5],
#     ["Sydney", 2058, 4336374, 1214.8],
#     ["Melbourne", 1566, 3806092, 646.9],
#     ["Perth", 5386, 1554769, 869.4],
# ]
table.add(headers, rows)
table.set_global_opts(
    title_opts=ComponentTitleOpts(
        title="Statistics of the Lexicon", 
        subtitle="The data source and respective statistics including the \
            number of word with one/two/three/four/more-than-four Chinese characters etc.")
)
# table.render_notebook()
table.render("lexicon_stat.html")


# %%
bar = Bar(init_opts=opts.InitOpts(
    chart_id="id", 
    width="600PX", 
    theme=ThemeType.LIGHT, 
    bg_color="white"))
bar.add_xaxis([key for key, _ in data_source_word_cnt.items()])
bar.add_yaxis(None, [value for key, value in data_source_word_cnt.items()])
bar.set_global_opts(title_opts=opts.TitleOpts(title="#words of each dictionary", subtitle=None))
bar.reversal_axis()
bar.set_series_opts(label_opts=opts.LabelOpts(position="right"))
bar.render_notebook()

# %%



