# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BatdongsanSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    name = scrapy.Field()
    mobile = scrapy.Field()
    address = scrapy.Field()
    lat = scrapy.Field()
    lon = scrapy.Field()
    short_info = scrapy.Field()
    
    Duong_vao = scrapy.Field()
    Huong_nha = scrapy.Field()
    Huong_ban_cong = scrapy.Field()
    So_tang = scrapy.Field()
    So_phong_ngu = scrapy.Field()
    So_toilet = scrapy.Field()
    Noi_that = scrapy.Field()
    Phap_ly = scrapy.Field()
    Mat_tien = scrapy.Field()
    Loai_tin_dang = scrapy.Field()
    Muc_gia = scrapy.Field()
    Dien_tich = scrapy.Field()
    Phong_ngu = scrapy.Field()
    Dia_chi = scrapy.Field()
    Ten_du_an = scrapy.Field()
    Chu_dau_tu = scrapy.Field()
    Quy_mo = scrapy.Field()
    
    
class AlonhadatSpiderItem(scrapy.Item):
    post_id = scrapy.Field()
    url = scrapy.Field()
    author = scrapy.Field()
    post_time = scrapy.Field()
    title = scrapy.Field()
    location = scrapy.Field()
    area = scrapy.Field()
    price = scrapy.Field()
    transaction_type = scrapy.Field()
    house_type = scrapy.Field()
    description = scrapy.Field()
    project = scrapy.Field()
    bedcount = scrapy.Field()
    
    
