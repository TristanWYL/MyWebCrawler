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
from git.repo.base import Repo


class CanCLID(scrapy.Spider):
    name = 'canclid'
    start_urls = ['https://github.com/CanCLID']

    def __init__(self, name=None, **kwargs):
        super(CanCLID, self).__init__(name, **kwargs)
        # initialize the directory for output
        self.output_dir = Path.joinpath(Path(os.path.dirname(os.path.realpath(__file__))).parent, "output", self.name)
        os.makedirs(self.output_dir, exist_ok=True)

    def parse(self, response, **kwargs):
        # inspect_response(response, self)
        links = response.xpath('/html/body/div/main/div/div/div/div/div[@class="org-repos repo-list"]/ul/li/div/div/h3[@class="wb-break-all"]/a[@data-hovercard-type="repository"]/@href').getall()
        for link in links:
            l = urljoin(self.start_urls[0], link)
            dir = Path.joinpath(self.output_dir, l.split('/')[-1])
            os.makedirs(dir, exist_ok=True)
            Repo.clone_from(l, dir, branch='master')




