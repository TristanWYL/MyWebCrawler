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


class Hanyu(scrapy.Spider):
    name = 'hanyu'
    start_urls = ["https://apps.itsc.cuhk.edu.hk/hanyu/Page/Terms.aspx"]
    isFirstWritten = True
    data = []

    def __init__(self, name=None, **kwargs):
        super(Hanyu, self).__init__(name, **kwargs)
        # initialize the directory for output
        self.output_dir = Path.joinpath(Path(os.path.dirname(os.path.realpath(__file__))).parent, "output", self.name)
        os.makedirs(self.output_dir, exist_ok=True)

    def parse(self, response, **kwargs):
        # inspect_response(response, self)
        category_urls = response.xpath('/html/body//div/table//tr/td/table/tbody/tr/td/a[@href]/@href').getall()
        for sub_category_url in category_urls:
            category_url = urljoin(self.start_urls[0], sub_category_url)
            yield scrapy.Request(category_url, callback=self.category_process)

    def category_process(self, response):
        category_word_urls = response.xpath('/html/body//div[@id="MainContent_panelTermsQuery"]/table[1]//tr/td/a[@href]/@href').getall() 
        for word_url_sub in category_word_urls:
            word_url = urljoin(self.start_urls[0], word_url_sub)
            yield scrapy.Request(word_url, callback=self.word_process)

    def word_process(self, response):
        word_info = dict()
        word_info['word'] = response.xpath('/html/body/div/div/div/table/tr[4]/td[1]/font/b/span/text()').get() 
        jyutpings_without_tone = response.xpath('/html/body/div/div/div/table/tr[4]/td[2]/font/span/text()').get().split()
        tone = response.xpath('/html/body/div/div/div/table/tr[4]/td[3]/font/span/text()').get()
        pattern_for_tone = re.compile(r'(\d+(?:\*\d+)?(?:\(.+\))?)')
        jyutpings = []
        for idx, tone in enumerate(re.findall(pattern_for_tone, tone)):
            jyutping = jyutpings_without_tone[idx] + tone
            jyutpings.append(jyutping)
        word_info['jyutping'] = " ".join(jyutpings)
        word_info['explanation'] = response.xpath('/html/body/div[2]/div[2]/div[1]/div[@class="searchResultTranslation"]/div/font/span/text()').getall()
        word_info['remark'] = response.xpath('/html/body/div[2]/div[2]/div[1]/div[@class="searchResultRemark"]/div/font/span/text()').get()
        self.data.append(word_info)

    def close(self, reason):
        # write the data to the output file
        filename = Path.joinpath(self.output_dir, "%s.json" % self.name)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
