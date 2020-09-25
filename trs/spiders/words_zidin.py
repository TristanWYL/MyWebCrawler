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


class WordsZidinSpider(scrapy.Spider):
    name = 'words_zidin'
    start_urls = ['https://words.hk/zidin/']
    isFirstWritten = True
    data = []

    def __init__(self, name=None, **kwargs):
        super(WordsZidinSpider, self).__init__(name, **kwargs)
        # initialize the directory for output
        self.output_dir = Path.joinpath(Path(os.path.dirname(os.path.realpath(__file__))).parent, "output", self.name)
        os.makedirs(self.output_dir, exist_ok=True)

    def parse(self, response, **kwargs):
        # yield scrapy.Request("https://words.hk/zidin/%E5%A2%9F", callback=self.word_process)
        words_link = response.xpath('/html/body//table/tbody/tr[@class="zi-item"]/td[1]/a/@href').getall()
        for word_link in words_link:
            link = urljoin(self.start_urls[0], word_link)
            yield scrapy.Request(link, callback=self.word_process)
        next_url_sub = response.xpath("/html/body/div/div/a[@class='paginate-next btn btn-default']/@href").get()
        if next_url_sub is not None and len(next_url_sub) > 0:
            next_url = urljoin(self.start_urls[0], next_url_sub)
            yield scrapy.Request(next_url, callback=self.parse)

    def word_process(self, response):
        # inspect_response(response, self)
        word_meanings_html = response.xpath('/html/body/div/div[@class="row"]/div/div[@class="row"]/div[@class="published-version"]')
        if len(word_meanings_html) == 0:
            return
        words_info = dict()
        words_info['word'] = response.xpath('/html/body/div[2]/div[2]/div[1]/div/div[1]/h1/text()').get().strip('「」')
        words_info['info'] = []
        for word_meaning_html in word_meanings_html:
            word_info = dict()
            jyutping = word_meaning_html.xpath('./table/tbody/tr/td/span[@class="zi-pronunciation"]//text()').getall()
            jyutping = [txt for txt in (txt.strip() for txt in jyutping) if txt]
            texts = word_meaning_html.xpath('./table/tbody/tr[@class="zidin-explanation"]/td[2]//div[parent::*[not(@*)]][1]//text()').getall()
            Chinese_explain, English_explain = "", ""
            if 'yue' in texts[0]:
                Chinese_explain = texts[1:]
                Chinese_explain = ''.join([item.strip() for item in Chinese_explain])
            texts = word_meaning_html.xpath('./table/tbody/tr[@class="zidin-explanation"]/td[2]//div[parent::*[not(@*)]][2]//text()').getall()
            if 'eng' in texts[0]:
                English_explain = texts[1:]
                English_explain = ''.join([item.strip() for item in English_explain])
            pos = word_meaning_html.xpath('./table/tbody/tr[2]/td[2]/span/text()').get()
            word_info['pos'] = pos
            word_info['jyutping'] = jyutping
            word_info['explain'] = {"Chinese":Chinese_explain, "English":English_explain}
            example_nodes = word_meaning_html.xpath('./table/tbody/tr/td//div[@class="zi-details-example-item"]')
            examples = []
            for node in example_nodes:
                samples = {}
                for idx, _ in enumerate(node.xpath('./div').getall(), 1):
                    texts = node.xpath('./div[{}]//text()'.format(idx)).getall()
                    sample = "".join([text.strip() for text in texts[1:]])
                    if 'yue' in texts[0]:
                        samples["Chinese"] = sample
                    elif 'eng' in texts[0]:
                        samples["English"] = sample
                examples.append(samples)
            word_info['examples'] = examples
            phrases_node = word_meaning_html.xpath(
                './table/tbody/tr[@class="zidin-explanation"]/td[2]//div[@class="zi-details-phrase-item"]')
            phrases = []
            for node in phrases_node:
                samples = {}
                for idx, _ in enumerate(node.xpath('./div').getall(), 1):
                    texts = node.xpath('./div[{}]//text()'.format(idx)).getall()
                    sample = "".join([text.strip() for text in texts[1:]])
                    if 'yue' in texts[0]:
                        samples["Chinese"] = sample
                    elif 'eng' in texts[0]:
                        samples["English"] = sample
                phrases.append(samples)
            word_info['phrases'] = phrases
            similar = word_meaning_html.xpath(
                './table/tbody/tr[@class="zidin-similar"]/td[2]/a[@href]/text()').getall()
            words_info['similar'] = similar
            words_info['info'].append(word_info)
        self.data.append(words_info)

    def close(self, reason):
        # write the data to the output file
        filename = Path.joinpath(self.output_dir, "%s.json" % self.name)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
