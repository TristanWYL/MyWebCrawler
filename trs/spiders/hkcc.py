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

class Progress(Enum):
    Login = 1,
    GetActors = 2,
    Crawl = 3


class HKCC_Spider(scrapy.Spider):
    name = 'hkcc'
    actors_url = 'https://hkcc.eduhk.hk/v1/corpus/'
    corpus_of_actor_url = 'https://hkcc.eduhk.hk/v1/corpus/actor_concordance.php?actorid='
    start_urls = ['https://hkcc.eduhk.hk/v1/corpus/signin.php']
    progress = Progress.Login
    actor_ids = None
    isFirstWritten = True

    def __init__(self, name=None, **kwargs):
        super(HKCC_Spider, self).__init__(name, **kwargs)
        # initialize the directory for output
        self.output_dir = Path.joinpath(Path(os.path.dirname(os.path.realpath(__file__))).parent, "output", self.name)

    def parse(self, response, **kwargs):
        if self.progress == Progress.Login:
            yield FormRequest.from_response(response,
                                         formdata={"username": "Tristan",
                                                   "password": "c187d88805ff59a4815236e15be691b5"},
                                         callback=self.login_response)
        elif self.progress == Progress.GetActors:
            self.get_actors_id(response)
            self.progress = Progress.Crawl
            for actor_id in self.actor_ids:
                url = self.corpus_of_actor_url + str(actor_id)
                yield scrapy.Request(url, callback=self.parse)
        elif self.progress == Progress.Crawl:
            list_corpus_of_one_actor = response.xpath('/html/body/table[2]//tr/td[4]/div/a/text()').getall()
            filename = Path.joinpath(self.output_dir, "%s.txt" % self.name)
            if self.isFirstWritten:
                if os.path.exists(filename):
                    os.remove(filename)
                self.isFirstWritten = False
            with open(filename, 'a+', encoding='utf-8') as f:
                for line in list_corpus_of_one_actor:
                    # codec = chardet.detect(line.encode())['encoding']
                    f.write(f'{line.strip()}\n')

    def login_response(self, response):
        if response.status == 200:
            self.progress = Progress.GetActors
            yield scrapy.Request(self.actors_url, callback=self.parse)

    def get_actors_id(self, response=None):
        self.actor_ids = response.xpath('//*[@id="actor_list"]/optgroup[1]/option/@value').getall()
        self.actor_ids += response.xpath('//*[@id="actor_list"]/optgroup[2]/option/@value').getall()

# from scrapy.shell import inspect_response
#         inspect_response(response, self)
# response.xpath("//td[contains(text(), '爸')]")