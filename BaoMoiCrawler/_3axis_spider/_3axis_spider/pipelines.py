# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from _3axis_spider.exporters import CsvCustomSeperator
import csv
from scrapy.exporters import CsvItemExporter
from datetime import date
from scrapy.pipelines.images import ImagesPipeline
import scrapy

class AxisSpiderPipeline(object):
    def __init__(self):
        # self.file = open("batdongsan-{}.csv".format(date.today().strftime("%Y-%m-%d")), 'wb+')
        print('#'* 40, " begin ", '#'* 40)
        self.file = ""
        self.exporter = ""

    def process_item(self, item, spider):
        print('#'* 40, spider.name, '#'* 40)
        
        # self.file = open("3axis-{}.csv".format(date.today().strftime("%Y-%m-%d")), 'wb+')
        self.file = open("{0}.csv".format(spider.name), "ab+")
        self.exporter = CsvCustomSeperator(self.file)
        self.exporter.start_exporting()

        self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()


    
class AxisSpiderImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        return [scrapy.Request(x, meta={'image_name': item["image_name"]})
                for x in item.get('image_urls', [])]

    def file_path(self, request, response=None, info=None):
        return '%s.jpg' % request.meta['image_name']        