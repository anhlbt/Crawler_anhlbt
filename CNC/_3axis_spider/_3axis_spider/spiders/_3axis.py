# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, ".")
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
    
from scrapy import Spider
from scrapy.http import Request
from _3axis_spider.items import AxisSpiderItem
from unidecode import unidecode
from utils.instalogger import InstaLogger
import re
import pdb
import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--dns-prefetch-disable')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--lang=en-US')
# chrome_options.add_argument('--headless')
chrome_options.add_argument('window-size=1920x1200')
downloadFilepath = '/media/pi/AnhLBT/DATASET/Scrapy_data/_3axis/cnc'
prefs = {'profile.default_content_setting_values.automatic_downloads': 1,\
    "profile.default_content_settings.popups":0, \
        "download.default_directory": downloadFilepath,\
        'intl.accept_languages': 'en-US'}
chrome_options.add_experimental_option('prefs',prefs) 
chrome_options.add_experimental_option("excludeSwitches", ['enable-automation']);    
browser = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', options=chrome_options)


def validate_field(field):
    if field:
        field.strip()
        field = field.replace("\r\n", "")
    else:
        field = ""
    return field


def check_link_exists():
    try:
        bds = pd.read_csv("./_3axis_spider.csv", sep='|')
        # link_exist = list(bds['url'].apply(lambda x: x.split("/")[-2]))
        link_exist = list(bds['image_name'])
        print("link_exist"*10)
        print(link_exist)
        return link_exist
    except Exception as ex:
        print(ex)
        return []

class AxisSpider(Spider):
    name = '_3axis_spider'
    link_exist = check_link_exists()
    allowed_domains = ['3axis.co']
    # start_urls = ['https://3axis.co/'] # replace start_requests
    next_page_number = 2
    
    def start_requests(self):
        urls = ['https://3axis.co/']
        for url in urls:
            yield Request(url=url, callback=self.parse, method="POST")   
     

    def parse(self, response):
        # pdb.set_trace()
        # self.link_exist = check_link_exists()
        type_urls = response.xpath('//*[@class="post-tags-list"]/ul/li/a/@href').extract() # list of link
        for type_url in type_urls[:-1]:
            self.next_page_number = 2
            type_url = response.urljoin(type_url)
            yield Request(type_url, callback=self.parse_pages,encoding = 'utf-8', method='POST')
 

    def parse_pages(self, response):
        item_urls = response.xpath('//*[@class="cont"]//*[@class="post-item"]/div/a/@href').extract() # list of items
        # pdb.set_trace()
        download_items = []
        download_items = [item.split('/')[-1] for item in item_urls]
        text = response.xpath('//*[@class="desc"]/text()').extract()[0]
        total_number = [int(s) for s in text.split() if s.isdigit()][0]
        print(self.link_exist)
        for item in download_items:
            if item not in self.link_exist:
                item_url = "https://3axis.co/download/" + item
                yield Request(item_url, callback=self.parse_info,meta={'item_url': item}, method='POST')
            else:
                print("+" * 100)
                print("{0} already exist".format(item))   
        try:
            if (self.next_page_number <= total_number/20):
                if '/dxf-files' in response.request.url:
                    absolute_next_page_url = 'https://3axis.co/dxf-files/page/' + str(self.next_page_number)
                elif '/free-cdr-files' in response.request.url:
                    absolute_next_page_url = 'https://3axis.co/free-cdr-files/page/' + str(self.next_page_number)
                InstaLogger.logger().info('absolute_next_page_url: %s - %s, ' %(absolute_next_page_url, response.request.url))
                yield Request(absolute_next_page_url, callback=self.parse_pages , method='POST')
                self.next_page_number = self.next_page_number + 1
        except Exception as ex:
            InstaLogger.logger().error('error: %s, ' %(ex))

    def parse_info(self, response):
        item = AxisSpiderItem()
        actions = ActionChains(browser)
        # pdb.set_trace()
        name = response.xpath('//*[@class="resp"]/text()').extract()
     
        item['url'] = response.request.url
        item['name'] = validate_field(name[0])
        item['image_urls']= response.xpath('//*[@class="main-image"]/img/@src').extract()
        item["image_name"]= response.meta.get('item_url')
        
        browser.get(response.url)
        
        next = browser.find_element_by_xpath('//*[@id="dl-button"]') #//*[@id="dl-button"]
        try:
            actions.click(next).perform()
            # next.click()
            browser.implicitly_wait(6)
            time.sleep(10)
            InstaLogger.logger().info('done: %s - %s, ' %(item['name'], item['url'].split('/')[-2]))

            # get the data and write it to scrapy items
        except Exception as ex:
            InstaLogger.logger().error('error: %s, ' %(ex))
        InstaLogger.logger().info(item)    
        yield item
        