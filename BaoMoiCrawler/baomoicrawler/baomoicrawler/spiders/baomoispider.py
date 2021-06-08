# -*- coding: utf-8 -*-
from scrapy import Request, Spider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from baomoicrawler.items import BaomoicrawlerItem
from scrapy.exceptions import CloseSpider
import pdb
import requests
from unidecode import unidecode
from os.path import join
import pandas as pd

class BaomoispiderSpider(CrawlSpider):
    name = 'baomoispider'
    audio_f = 'audio'
    allowed_domains = ['baomoi.com']
    start_urls = ['https://baomoi.com']
    crawled_link= []
    with open("link.txt", "r") as f:
        for line in f.readlines():
            start_urls.append(line.strip())
    f.close()
    
    with open("crawled_link.txt", "r") as f:
        for line in f.readlines():
            crawled_link.append(line.strip())
    f.close()

    # pdb.set_trace()
    MAX = 50 #maximum number article
    count = 0
    rules = (Rule(LinkExtractor(restrict_xpaths=('//*[@class="pagination__controls"]'), \
        deny=('\S+/c/\S+','\S+/t/\S+', '\S+/trang\d{3,}.epi', '\S+/trang([4-9]\d|\d{3,}).epi')), \
            callback="parse_items",follow= True),)
    
    def parse_items(self, response):
        # pdb.set_trace()
        urls = response.xpath('//*[@class="cache"]/@href')
        for url in urls:
            connect_to_url = response.urljoin(url.extract())
            yield Request(connect_to_url, callback=self.parse_question)

    def parse_question(self, response):
        # pdb.set_trace()
        item = BaomoicrawlerItem()
        #item['title']
        item['title'] = response.xpath('//*[@class="article__header"]/text()').extract_first().strip()
        if item['title'] in self.crawled_link:
            # pdb.set_trace()
            print("Exists %s"%item['title'])
            return
        
        audio_name = response.request.url.split('/')[-1].split('.')[0]
        item['topic'] = response.xpath('//*[@class="cate"]/text()').extract_first().strip()
        topic = unidecode(item['topic']).replace(' ', '_')
        item['audio_links'] = list(set(response.xpath('//*[@class="tts-player"]//@data-src').extract()))
        item['image'] = response.xpath('//*[@class="body-image"]//@src').extract()
        item['timestamp'] = response.xpath('//*[@class="time"]/text()').extract_first().strip()
        #item['summary'] 
        item['summary']= response.xpath('//*[@class="article__sapo"]/text()').extract_first().strip()
        #in contents field, we get text body, <strong> <url of image>, <em>, insert all into db but remove field url of images in  elastic
        contents = response.xpath('//*[@class="body-text"]/text() | //*[@class="body-text"]/strong | \
            //*[@class="body-image"]//@src | //*[@class="body-text media-caption"]/em | \
                //*[@class="body-text"]/em').extract() #article__sapo
        contents = [content.strip() for content in contents]
        item['body'] ="\t\n\n".join(contents)
        
        tags = response.xpath('//*[@class="keyword"]/text()').extract()
        tags = [tag.strip()for tag in tags]
        item['tags'] = ", ".join(tags) 
        
        item['link_'] =response.request.url
        
        source = response.xpath('//*[@class="article__meta"]/a[@class="source"]/text()').extract() 
        source = [s.strip() for s in source]
        source = "".join(source)
        source_link = response.xpath('//*[@class="bm-source"]/a/@href').extract_first()
        # full_source_link = response.urljoin(source_link)
        item['source'] = (source + ': ' + source_link)
        
        self.count += 1
        if self.count > self.MAX:
            raise CloseSpider('20000 pages crawled')

        yield item

