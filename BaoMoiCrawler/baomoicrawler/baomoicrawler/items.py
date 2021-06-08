# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaomoicrawlerItem(scrapy.Item):
    title = scrapy.Field()
    summary = scrapy.Field()
    timestamp = scrapy.Field()
    tags = scrapy.Field()
    body = scrapy.Field()
    link_ = scrapy.Field()
    topic = scrapy.Field()
    source = scrapy.Field()
    audio_links = scrapy.Field()
    image = scrapy.Field()


