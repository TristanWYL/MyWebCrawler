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


class WongtaksumSpider(scrapy.Spider):
    name = 'wongtaksum'
    start_urls = ['http://wongtaksum.no-ip.info:81/corpus.htm']
    isFirstWritten = True
    table_names = ["Cantonese Discourse Data", "Cantonese Debates Hosted by RTHK", "Mandarin Discourse Data"]

    def __init__(self, name=None, **kwargs):
        super(WongtaksumSpider, self).__init__(name, **kwargs)
        # initialize the directory for output
        self.output_dir = Path.joinpath(Path(os.path.dirname(os.path.realpath(__file__))).parent, "output", self.name)

    def parse(self, response, **kwargs):
        # inspect_response(response, self)
        for i, table_name in enumerate(self.table_names):
            dir_sub = table_name.replace(" ", "")
            output_dir_sub = Path.joinpath(self.output_dir, dir_sub)
            os.makedirs(output_dir_sub, exist_ok=True)
            xpath_url = '//table[{}]//a/@href'.format(i+1)
            file_urls = response.xpath(xpath_url).getall()
            for file_url in file_urls:
                url = urljoin(self.start_urls[0], file_url)
                file_name = os.path.join(output_dir_sub, file_url.split("/")[-1])
                if not os.path.exists(file_name):
                    try:
                        urlretrieve(url, file_name)
                    except Exception as e:
                        print(e)
                        print("url: {}, file name: {}".format(url, file_name))

