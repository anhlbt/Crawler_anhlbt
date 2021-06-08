# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sys 
sys.path.insert(0,"../")
import logging
import pymongo
import os
import pdb
from scrapy.exceptions import DropItem
# from baomoicrawler.exporters import JsonItemExporter
import json, codecs
from scrapy.exceptions import CloseSpider
from elasticsearch import Elasticsearch
from unidecode import unidecode
from os.path import join, isdir
import requests
from datetime import datetime
import re
import json 
from sqlalchemy import Column, Integer, String, Text, DateTime
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext import mutable
# from sqlalchemy.dialects import postgresql
from utils.db import *
from utils.instalogger import InstaLogger

mutable.MutableDict.associate_with(JsonEncodedDict)

#write data to file json
class BaomoicrawlerPipeline(object):
    def __init__(self):
        self.file = codecs.open("data_week_temp.json", 'w', encoding="utf-8")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False, indent=4) + ",\n"
        self.file.write(line)
        return item

# processing save audio
class Baomoicrawledfile(object):
    def __init__(self, audio_path):
        self.file = codecs.open("crawled_link.txt", 'r+', encoding="utf-8")
        self.lst_title = self.file.read()
        self.audio_path = audio_path

    def close_spider(self, spider):
        self.file.close()
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            audio_path=crawler.settings.get('AUDIO_PATH'),

        )

    def process_item(self, item, spider):
        if item['title'] not in self.lst_title:
            self.file.write(item['title'] + "\n")
            
            set_audio_files = set([d[:-2] for d in os.listdir(self.audio_path) if not isdir(join(self.audio_path, d))])
            
            if len(item['audio_links']) > 1:
                # title_num = item['link'].split('/')[-1].split('.')[0]
                title = unidecode(item['title']).replace(' ', '_')
                topic = unidecode(item['topic']).replace(' ', '_')
                topic = re.sub(r'[^a-zA-Z0-9_-]', '', topic)    
                title = re.sub(r'[^a-zA-Z0-9_-]', '', title)
                if "{0}_{1}".format(topic, title) not in set_audio_files:
                    # pdb.set_trace()
                    # timestamp = int(datetime.timestamp(datetime.strptime(item["time"][:14], '%d/%m/%y %H:%M')))
                    for i, link in enumerate(item['audio_links']):
                        engine = link.split('&')[-1].split("=")[-1]
                        audio_f = topic+'_'+title+'_'+engine
                        tmp_file = requests.get(link)
                        with open(join(self.audio_path, audio_f), 'wb') as f:
                            f.write(tmp_file.content)
                        f.close()        
        return item
    

#not implement
class MongoPipeline(object):
    collection_name = os.environ.get('CRAWLAB_COLLECTION')

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        dup_check = self.db[self.collection_name].find(
            {'url': item['url']}).count()
        if dup_check == 0:
            if item['title'] != '':
                item['task_id'] = os.environ.get('CRAWLAB_TASK_ID')
                self.db[self.collection_name].insert_one(dict(item))

                logging.debug("--- ADDED ---")
        else:
            logging.debug("--- EXISTED ---")

        return item

#save data into db (elasticsearch and sqlite or something)
class ElasticPipeline():
    def __init__(self,host, port, index):
        self.es_host = host
        self.es_port = port
        self.es_index = index
        self.file = codecs.open("crawled_link.txt", 'r+', encoding="utf-8")
        self.lst_title = self.file.read()
        # self.es = self.connect_elasticsearch()
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('ES_HOST'),
            port=crawler.settings.get('ES_PORT'),
            index=crawler.settings.get('ES_INDEX')
        )    
        
    def open_spider(self, spider):
        self.es = self.connect_elasticsearch()
    
    def connect_elasticsearch(self):
        _es = None
        _es = Elasticsearch([{'host': self.es_host, 'port': self.es_port}])
        if _es.ping():
            print('Elastic Connected')
        else:
            print('Ec Ec, it could not connect!')
        return _es    
    
    def close_spider(self, spider):
        self.file.close()
        # self.es.transport.close()

            
    def search(self, search):
        res = self.es.search(index=self.es_index, body=search)
        return res

    def store_record(self, record, id):
        is_stored = True
        try:
            outcome = self.es.index(index=self.es_index, doc_type='baomoi', body=record, id = id)
        except Exception as ex:
            print('Error in indexing data', str(ex))
            InstaLogger.logger().error(ex)
            is_stored = False
        finally:
            return is_stored

    def process_item(self, item, spider):
        # pdb.set_trace()
        if item['title'] not in self.lst_title:
            self.file.write(item['title'] + "\n")
            
            audio_name = item['link_'].split('/')[-1].split('.')[0]
            topic = unidecode(item['topic']).replace(' ', '_')
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', item['body'])
            # #insert markdown to show image
            for img_url in urls:
                # db_body = item['body'].replace(img_url, "\n![{0}]({1})\n".format(item['source'], img_url))
                item['body'] = item['body'].replace(img_url, "\n ![]({0})".format(img_url))            
            
            #insert into db (sqlite or any kind of)
            # dbms = MyDatabase('SQLITE', dbname='app.db')
            dbms = MyDatabase('POSTGRESQL', username='superset', password='superset',dbname='baomoi.psql')
            post = dict(item)
            
            try:
                dbms.add_post(Post(title=post['title'], summary=post['summary'], link_ = post['link_'],\
                    body=item['body'], image=post['image'], tags = post['tags'],\
                        topic = post['topic'],source = post['source'],audio_links = post['audio_links'], author_id = 1))
            except Exception as e:
                InstaLogger.logger().error(e)  
            
            #remove url of images
            for img_url in urls:    
                item['body'] = item['body'].replace("\n ![]({0})".format(img_url), "\n")
            #insert into elastic
            if self.es is not None:
                out = self.store_record(dict(item), topic+'_'+audio_name)
                print('Data indexed successfully')
                 
        # return item


    
# if __name__=="__main__":
#     json_path = './tmp/a3.json'
#     json_book = load_json_from_file(json_path)
#     # dbms = MyDatabase('SQLITE', dbname='app.db')
#     dbms = MyDatabase('POSTGRESQL', username='superset', password='superset',dbname='baomoi.psql')

#     post = Post(id=22222, title='auto title', summary="auto summary", body = "auto body", json_book = json_book, author_id = 1)
#     dbms.add_post(post)
    
#     print("  ")
       