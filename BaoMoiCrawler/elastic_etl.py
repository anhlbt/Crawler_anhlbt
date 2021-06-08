import json
import logging
from pprint import pprint
from time import sleep
import json
from elasticsearch import Elasticsearch
from unidecode import unidecode
import pdb
import random
from os.path import isdir, join, exists
import os, re
from alignment.config import Config

config = Config('config.ini')


def search(es_object, index_name, search):
    res = es_object.search(index=index_name, body=search)
    return res


def create_index(es_object, index_name):
    created = False
    
    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1
        },
        "mappings": {
            "baomoi2": {
                "dynamic": False,
                "properties": {
                    "topic": {
                        "type": "text"
                    },
                    "audio_links": {
                        "type": "Arrays"
                    },
                    "title": {
                        "type": "text"
                    },
                    "time": {
                        "type": "text"
                    },
					"summary": {
                        "type": "text"
                    },
					"content": {
                        "type": "text"
                    },
                    "link": {
                        "type": "text"
                  
                    },
                }
            }
        }
    }

    try:
        if not es_object.indices.exists(index_name):
            # Ignore 400 means to ignore "Index Already Exist" error.
            es_object.indices.create(index=index_name, ignore=400, body=settings)
            print('Created Index')
        created = True
    except Exception as ex:
        print(str(ex))
    finally:
        return created


def store_record(elastic_object, index_name, record, id):
    # pdb.set_trace()
    is_stored = True
    try:
        outcome = elastic_object.index(index=index_name, doc_type='baomoi2', body=record, id = id)
    except Exception as ex:
        print('Error in indexing data')
        print(str(ex))
        is_stored = False
    finally:
        return is_stored


def connect_elasticsearch():
    _es = None
    _es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if _es.ping():
        print('Yay Connected')
    else:
        print('Awww it could not connect!')
    return _es


 
def load_json_to_es(es, json_path):
    with open("baomoicrawler/data_week_temp.json", "r") as f:
        data = f.read()
        data = json.loads(data)

        if (len(data) > 1):
            for d in data[:10]:
                audio_name = d['link'].split('/')[-1].split('.')[0]
                topic = unidecode(d['topic']).replace(' ', '_')
                # res = es.index(index="baomoi2", doc_type="json", id=topic+'_'+audio_name, body=d)
                if es is not None:
                    # pdb.set_trace()
                    if create_index(es, 'baomoi2'):
                        out = store_record(es, 'baomoi2', d, topic+'_'+audio_name)
                        print('Data indexed successfully')

def export_text_from_es(es, text_folder, audio_folder):
    res = es.search(index='baomoi', body={
        "from" : 0, "size" : 1000,
        "_source": ["topic", "title", "summary", "content"], 
        "query": {
            "bool": {
            "must": [{
                "exists": {
                    "field": "audio_links"
                    }
                }]
            }
            }
        })

    print(res['hits']['total']['value'])
    
    # audio_dir = '/media/anhlbt/AnhLBT/DATASET/NLP_dataset/Baomoi/Audio'
    lst_audio_files = list(set([d[:-2] for d in os.listdir(audio_folder) if not isdir(join(audio_folder, d))]))
    
    for doc in res['hits']['hits']:
        full_content =''
        title = unidecode(doc['_source']['title']).replace(' ', '_')
        topic = unidecode(doc['_source']['topic']).replace(' ', '_')
        topic = re.sub(r'[^a-zA-Z0-9_-]', '', topic)    
        title = re.sub(r'[^a-zA-Z0-9_-]', '', title)  
        if "{0}_{1}".format(topic, title) in lst_audio_files:
            full_content = doc['_source']['title'] + ". \n" + doc['_source']['summary'] + "\n" +doc['_source']['content']
            print(title)
            with open(join(text_folder, "{0}_{1}.txt".format(topic, title)) ,"w+") as script:
                script.write(full_content)
           


if __name__ == '__main__':

    
    text_folder = config.elastic['text_folder']
    audio_folder = config.elastic['audio_folder']
    if not exists(text_folder):
        os.makedirs(text_folder)
    if not exists(audio_folder):
        os.makedirs(audio_folder)
            
    es = connect_elasticsearch()
    export_text_from_es(es, text_folder, audio_folder)
    

        
    #some query...    
    # res = search(es,'baomoi2', json.dumps({'_source': ['title'],'query': {'match_all': {}}}))

    
    # res = es.search(index="baomoi", body={
    #                 "query": {"multi_match": {"query": "Park Ji-sung"}}})
    # res = es.search(index="baomoi", body={
    #                 "query": {
    #                     "multi_match": {
    #                         "query": "Hà Nội", 
    #                         "fields": ["title^3", "content"]
    #                         }
    #                     }
    #                 })

    # res = es.search(index="baomoi", body={
    #                 "from" : 0, "size" : 10000,
    #                 "query": {
    #                     "multi_match": {
    #                         "query": "Hà Nội", 
    #                         "type": "best_fields",
    #                         "fields": ["title^3", "content"],
    #                         "tie_breaker": 0.3
    #                         }
    #                     }
    #                 })


 
    
    # if es is not None:
    #     # search_object = {'query': {'match': {'calories': '102'}}}
    #     # search_object = {'_source': ['title'], 'query': {'match': {'calories': '102'}}}
    #     # search_object = {'_source': ['title'], 'query': {'range': {'calories': {'gte': 20}}}}
    #     search_object = {'_source': ['title'], 'query': {'match': {'content': "anh"}}}
    #     search(es, 'baomoi2', json.dumps(search_object))