# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy.http import Request
from batdongsan_spider.items import BatdongsanSpiderItem
from unidecode import unidecode
import re
import pdb
import pandas as pd



def validate_field(field):
    if field:
        field.strip()
        field = field.replace("\r\n", "")
    else:
        field = ""
    return field

def extrac_latlon(field):
    if field:
        numregex = '[-+]?[0-9]{0,3}(?:(?:\.[0-9]+)|(?:[0-9]+))'
        pattern = '(' + numregex + ',' + numregex + ')'
        regex1 = re.compile(pattern)
        search = regex1.findall(field)
    return search[0]    

def check_link_exists():
    try:
        bds = pd.read_csv("./batdongsan.csv", sep='|')
        link_exist = list(bds['url'].apply(lambda x: x.split("batdongsan.com.vn")[-1]))
        print("link_exist"*10)
        print(link_exist)
        return link_exist
    except Exception as ex:
        print(ex)
        return []

class BatdongsanSpider(Spider):
    name = 'batdongsan'
    link_exist = []
    allowed_domains = ['batdongsan.com.vn']
    start_urls = ['http://batdongsan.com.vn/']
    # start_urls = ['https://batdongsan.com.vn/nha-dat-ban-binh-thuan']
    

    def parse(self, response):
        # pdb.set_trace()
        self.link_exist = check_link_exists()
        type_urls = response.xpath('//*[@class="dropdown-navigative-menu"]/li/a/@href')[2:3].extract()
        #type_urls = response.xpath('//*[@class="dropdown-navigative-menu"]/li/a/@href')[1:2].extract()
        # type_urls = ['https://batdongsan.com.vn/nha-dat-ban-binh-thuan']  #need change type_urls
        for type_url in type_urls:
            type_url = response.urljoin(type_url)
            yield Request(type_url, callback=self.parse_pages)
 

    def parse_pages(self, response):
        item_urls = response.xpath('//*[@class="wrap-plink"]/@href').extract()
        # pdb.set_trace()
        for item_url in item_urls:
            if item_url not in self.link_exist:
                item_url = response.urljoin(item_url)
                yield Request(item_url, callback=self.parse_info)
            else:
                print("+" * 100)
                print("{0} already exist".format(item_url))   
        next_page_number = 2 

        try:
            while(next_page_number < 8889):
                if '/nha-dat-ban' in response.request.url:
                    # absolute_next_page_url = 'https://batdongsan.com.vn/nha-dat-ban-binh-thuan/p' + str(next_page_number)
                    absolute_next_page_url = 'https://batdongsan.com.vn/nha-dat-ban/p' + str(next_page_number)
                elif '/nha-dat-cho-thue' in response.request.url:
                    # absolute_next_page_url = 'https://batdongsan.com.vn/nha-dat-ban-binh-thuan/p' + str(next_page_number)
                    absolute_next_page_url = 'https://batdongsan.com.vn/nha-dat-cho-thue/p' + str(next_page_number)

                #absolute_next_page_url = 'https://batdongsan.com.vn/nha-dat-ban/p' + str(next_page_number)
                yield Request(absolute_next_page_url, callback=self.parse_pages)
                next_page_number = next_page_number + 1
        except:
            pass

    def parse_info(self, response):
        item = BatdongsanSpiderItem()
        # pdb.set_trace()
        name = response.xpath('//*[@class="name"]/text()').extract_first().strip()
        mobile = response.xpath('//*[@class="phoneEvent"]/text()').extract_first().strip()
        address = response.xpath('//*[@class="short-detail"]/text()').extract_first().strip()
        latlon = response.xpath('//*[@class="map"]//@src').extract_first().strip()
        short_info = response.xpath('//*[@class="short-detail-2 list2 clearfix"]//*[@class="sp3"]/text()').extract() #dateBegin_dateEnd_newsType_newsCode
        title2 = response.xpath('//*[@class="box-round-grey3"]//*[@class="row-1"]//*[@class="r1"]/text()').extract()
        value2 = response.xpath('//*[@class="box-round-grey3"]//*[@class="row-1"]//*[@class="r2"]/text()').extract()
        title1 = response.xpath('//*[@class="short-detail-2 clearfix pad-16"]//*[@class="sp1"]/text()').extract()
        value1 = response.xpath('//*[@class="short-detail-2 clearfix pad-16"]//*[@class="sp2"]/text()').extract() #list

        item['url'] = response.request.url
        item['name'] = validate_field(name)
        item['mobile'] = validate_field(mobile)
        item['address']=  validate_field(address)
        item['lat'] = extrac_latlon(latlon).split(",")[0]
        item['lon'] = extrac_latlon(latlon).split(",")[1]
        item['short_info'] = short_info
        
        for i in range(len(title1)):
            item[unidecode(title1[i]).replace(' ', '_').replace(':', '')]= value1[i]
        for i in range(len(title2)):
            item[unidecode(title2[i]).replace(' ', '_').replace(':', '')]= value2[i]        


        yield item