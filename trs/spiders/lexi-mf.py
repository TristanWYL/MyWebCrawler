import scrapy
from bs4 import BeautifulSoup
from pathlib import Path
from scrapy import Request
from scrapy.http import FormRequest
from scrapy.utils.response import open_in_browser
from enum import Enum
import os
import chardet
from scrapy.shell import inspect_response
from urllib.request import urlretrieve
from urllib.parse import urljoin
import json
import re


class LexiMfSpider(scrapy.Spider):
    name = 'lexi_mf'
    start_urls = ["https://humanum.arts.cuhk.edu.hk/Lexis/lexi-mf/stroke.php"]
    isFirstWritten = True
    data = []
    pattern = re.compile(
        'phonetic_initial\[\d*\]\s*=\s*\"(.*?)\";\\r\\n\\tphonetic_final\[\d*\]\s*=\s*\"(.*?)\";\\r\\n\\tphonetic_tone\[\d*\]\s*=\s*\"(.*?)\"')

    def __init__(self, name=None, **kwargs):
        super(LexiMfSpider, self).__init__(name, **kwargs)
        # initialize the directory for output
        self.output_dir = Path.joinpath(Path(os.path.dirname(os.path.realpath(__file__))).parent, "output", self.name)
        os.makedirs(self.output_dir, exist_ok=True)

    def parse(self, response, **kwargs):
        # inspect_response(response, self)
        num_stroke_urls = response.xpath('/html/body//table//table[@class="radical_table"]/tr/th/a[@href]/@href').getall()
        for sub_num_stroke_url in num_stroke_urls:
            num_stroke_url = self.start_urls[0] + sub_num_stroke_url
            yield scrapy.Request(num_stroke_url, callback=self.stroke_process)

    def stroke_process(self, response):
        # inspect_response(response, self)
        # yield scrapy.Request("https://humanum.arts.cuhk.edu.hk/Lexis/lexi-mf/search.php?word=%E4%B8%94", callback=self.word_process)
        words_of_strok_num = response.xpath('/html/body//table//table[@class="radical_table"]/tr/td/a[span]/@href').getall()
        for word in words_of_strok_num:
            word_url = urljoin(self.start_urls[0], word)
            yield scrapy.Request(word_url, callback=self.word_process)

    def word_process(self, response):
        # inspect_response(response, self)
        word_phonetics_html = response.xpath(
            '/html/body//table[@id="char_can_table"]/tr/td[@class="char_can_head"]/span[@id="phonetic_81"]')
        if len(word_phonetics_html) == 0:
            return
        words_info = dict()
        words_info['word'] = response.xpath('/html/body//table[@class="char_head_table"]/td/div[@id="char_headchar"]/text()').get().strip('')
        words_info['info'] = []
        word_meanings_html = response.xpath(
            '/html/body//table[@id="char_can_table"]/tr/td[@class="char_can_head"]')
        for ind, word_meaning_html in enumerate(word_meanings_html):
            word_info = dict()
            jyutping = word_meaning_html.xpath('./script//text()').get()
            for (initial, final, tone) in re.findall(self.pattern, jyutping):
                jyutping = "".join([initial.strip(), final.strip(), tone.strip()])
            # explain = word_meaning_html.xpath(
            #     './table/tbody/tr[@class="zidin-explanation"]/td[2]/div[1]//text()').getall()[1:]
            # explain = ''.join([item.strip() for item in explain])
            # pos = word_meaning_html.xpath('./table/tbody/tr[2]/td[2]/span/text()').get()
            # word_info['pos'] = pos
            word_info['jyutping'] = jyutping
            # word_info['explain'] = explain
            # example_nodes = word_meaning_html.xpath('./table/tbody/tr/td/div[@class="zi-details-example-item"]')
            # examples = []
            # for node in example_nodes:
            #     texts = node.xpath('./div[1]//text()').getall()
            #     example = "".join([text.strip() for text in texts[1:-1]])
            #     jyutping = texts[-1].strip("()")
            #     examples.append({"example": example, "jyutping": jyutping})
            examples = word_meaning_html.xpath('../td[@class="char_can_eg"]/div/text()').get().strip()
            word_info['examples'] = examples
            # phrases_node = word_meaning_html.xpath(
            #             #     './table/tbody/tr[@class="zidin-explanation"]/td[2]/div[@class="zi-details-phrase-item"]')
            #             # phrases = []
            #             # for node in phrases_node:
            #             #     texts = node.xpath('./div[1]//text()').getall()
            #             #     phrase = "".join([text.strip() for text in texts[1:-1]])
            #             #     jyutping = texts[-1].strip("()")
            #             #     phrases.append({"phrase": phrase, "jyutping": jyutping})
            #             # word_info['phrases'] = phrases
            #             # similar = word_meaning_html.xpath(
            #             #     './table/tbody/tr[@class="zidin-similar"]/td[2]/a[@href]/text()').getall()
            #             # words_info['similar'] = similar
            tr_ind = ind*3+4
            check_script = word_meaning_html.xpath('../../tr[{}]/td[@class="char_can_note"]/script'.format(tr_ind))
            jp = None
            note = ""
            if check_script:
                text = check_script.xpath('./text()').get()
                for (initial, final, tone) in re.findall(self.pattern, text):
                    jp = "".join([initial.strip(), final.strip(), tone.strip()])
                text_around = word_meaning_html.xpath('../../tr[{}]/td[@class="char_can_note"]/text()'.format(tr_ind)).getall()
                if text_around == []:
                    note = jp
                else:
                    text_around.insert(1,jp)
                    note = "".join(text_around)
            else:
                notes = word_meaning_html.xpath('../../tr[{}]/td[@class="char_can_note"]//text()'.format(tr_ind)).getall()
                if notes:
                    note = "".join([n.strip() for n in notes])
            word_info['note'] = note
            words_info['info'].append(word_info)
        self.data.append(words_info)

    def close(self, reason):
        # write the data to the output file
        filename = Path.joinpath(self.output_dir, "%s.json" % self.name)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
