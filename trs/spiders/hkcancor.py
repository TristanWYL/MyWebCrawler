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


class HKCanCorSpider(scrapy.Spider):
    name = 'hkcancor'
    start_urls = ['http://compling.hss.ntu.edu.sg/hkcancor/']
    isFirstWritten = True

    def __init__(self, name=None, **kwargs):
        super(HKCanCorSpider, self).__init__(name, **kwargs)
        # initialize the directory for output
        self.output_dir = Path.joinpath(Path(os.path.dirname(os.path.realpath(__file__))).parent, "output", self.name)
        os.makedirs(self.output_dir, exist_ok=True)

    def parse(self, response, **kwargs):
        # inspect_response(response, self)
        xpath_url = '/html/body/ul[1]/li/a/@href'
        file_urls = response.xpath(xpath_url).getall()
        for file_url in file_urls:
            url = urljoin(self.start_urls[0], file_url)
            file_name = os.path.join(self.output_dir, file_url)
            # create directory if inexistence
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            if not os.path.exists(file_name):
                try:
                    urlretrieve(url, file_name)
                except Exception as e:
                    print(e)
                    print("url: {}, file name: {}".format(url, file_name))
