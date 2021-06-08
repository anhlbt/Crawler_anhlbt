# -*- coding: utf-8 -*-
import scrapy
import pdb
from lxml import html

class GetlinkSpider(scrapy.Spider):
    name = 'getlink'
    allowed_domains = ['baomoi.com']
    start_urls = ['https://baomoi.com/']

    def parse(self, response):
        # tree = (html.fromstring(response.text))
        # pdb.set_trace()
        # f2 = open("text", 'w')
        # f2.write(response.text)
        # f2.close()
        links = response.xpath('//*[@class="container"]/ul/li/a/@href').extract()
        links = [response.urljoin(link) for link in links if "epi" in link]
        with open("link.txt", "a") as f:
            for link in links:
                f.write(link)
                f.write("\n")
        f.close()

# links = response.xpath('/html/body/div[6]/div[4]/div/div[3]/div/div[1]/div[9]/a/h2').extract()


