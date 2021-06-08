**to run: scrapy crawl baomoispider**

config path to audio_folder in config.ini

#query empty audio_links
GET baomoi/_search
{
  "query": {
    "bool": {
      "must_not": [{
        "exists": {
	         "field": "audio_links"
        }
      }]
    }
  }
}



GET baomoi/_search
{"_source": ["audio_links", "title", "summary", "content"], 
  "query": {
    "bool": {
      "must": [{
        "exists": {
	         "field": "audio_links"
        }
      }]
    }
  }
}
