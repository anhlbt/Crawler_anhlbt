# -*- coding: utf-8 -*-
import scrapy
import datetime
import pdb

class VnexpressSpider(scrapy.Spider):
    name = 'vnexpress'
    allowed_domains = ['vnexpress.net']
    start_urls = [
        'https://vnexpress.net/the-gioi/tu-lieu',
        'https://vnexpress.net/the-gioi/phan-tich',
        'https://vnexpress.net/the-gioi/nguoi-viet-5-chau',
        'https://vnexpress.net/the-gioi/cuoc-song-do-day',
        'https://vnexpress.net/the-gioi/quan-su',
        'https://vnexpress.net/kinh-doanh/doanh-nghiep',
        'https://vnexpress.net/kinh-doanh/bat-dong-san',
        'https://vnexpress.net/kinh-doanh/ebank',
        'https://vnexpress.net/kinh-doanh/thuong-mai-dien-tu',
        'https://vnexpress.net/kinh-doanh/hang-hoa',
        'https://vnexpress.net/kinh-doanh/tien-cua-toi',
        'https://vnexpress.net/kinh-doanh/chung-khoan',
        'https://vnexpress.net/kinh-doanh/quoc-te',
        'https://vnexpress.net/kinh-doanh/vi-mo',
        'https://vnexpress.net/giai-tri/gioi-sao',
        'https://vnexpress.net/giai-tri/phim',
        'https://vnexpress.net/giai-tri/nhac',
        'https://vnexpress.net/giai-tri/thoi-trang',
        'https://vnexpress.net/giai-tri/lam-dep',
        'https://vnexpress.net/giai-tri/sach',
        'https://vnexpress.net/giai-tri/san-khau-my-thuat',
        'https://vnexpress.net/bong-da',
        'https://vnexpress.net/the-thao/tennis',
        'https://vnexpress.net/the-thao/cac-mon-khac',
        'https://vnexpress.net/the-thao/hau-truong',
        'https://vnexpress.net/the-thao/tuong-thuat',
        'https://vnexpress.net/phap-luat/ho-so-pha-an',
        'https://vnexpress.net/phap-luat/tu-van',
        'https://vnexpress.net/giao-duc/tuyen-sinh',
        'https://vnexpress.net/giao-duc/du-hoc',
        'https://vnexpress.net/giao-duc/giao-duc-40',
        'https://vnexpress.net/giao-duc/hoc-tieng-anh',
        'https://vnexpress.net/suc-khoe/tin-tuc',
        'https://vnexpress.net/suc-khoe/cac-benh',
        'https://vnexpress.net/suc-khoe/tu-van',
        'https://vnexpress.net/suc-khoe/khoe-dep',
        'https://vnexpress.net/suc-khoe/dan-ong',
        'https://vnexpress.net/suc-khoe/dinh-duong',
        'https://vnexpress.net/suc-khoe/ung-thu',
        'https://vnexpress.net/doi-song/to-am',
        'https://vnexpress.net/doi-song/bai-hoc-song',
        'https://vnexpress.net/doi-song/nha',
        'https://vnexpress.net/doi-song/tieu-dung',
        'https://vnexpress.net/du-lich/diem-den',
        'https://vnexpress.net/du-lich/dau-chan',
        'https://vnexpress.net/du-lich/tu-van',
        'https://vnexpress.net/khoa-hoc/trong-nuoc',
        'https://vnexpress.net/khoa-hoc/thuong-thuc',
        'https://vnexpress.net/khoa-hoc/the-gioi-dong-vat',
        'https://vnexpress.net/khoa-hoc/chuyen-la',
        'https://vnexpress.net/so-hoa/doi-song-so',
        'https://vnexpress.net/so-hoa/san-pham',
        'https://vnexpress.net/so-hoa/dien-tu-gia-dung',
        'https://vnexpress.net/so-hoa/kinh-nghiem',
        'https://vnexpress.net/oto-xe-may/tu-van',
        'https://vnexpress.net/oto-xe-may/thi-truong',
        'https://vnexpress.net/oto-xe-may/dien-dan',
        'https://vnexpress.net/oto-xe-may/xe-xanh',
        'https://vnexpress.net/oto-xe-may/danh-gia',
        'https://vnexpress.net/y-kien/thoi-su',
        'https://vnexpress.net/y-kien/doi-song',
        'https://vnexpress.net/cuoi/tieu-pham',
        'https://vnexpress.net/thoi-su/giao-thong',
        'https://vnexpress.net/thoi-su/mekong',
        'https://vnexpress.net/tuyen-dau-chong-dich'
    ]
    # exclude goc_nhin, startup, cam_nang, safe_go, tu_van

    def parse(self, response):
        # pdb.set_trace()
        top_link = response.css(
            '.item-news.full-thumb.article-topstory a::attr(href)').get()
        yield scrapy.Request(top_link, callback=self.parse_detail)

        detail_links = response.css(
            '.item-news-common > .title-news > a::attr(href)')
        yield from response.follow_all(detail_links, self.parse_detail)

        # follow all pagination links
        pagination_links = response.css('.next-page::attr(href)')
        yield from response.follow_all(pagination_links, self.parse)

    def parse_detail(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        metaTags = response.css('meta[name="its_tag"]').re(
            r'content="(.*)"')
        if len(metaTags) > 0:
            tags = [x.strip() for x in metaTags[0].split(',')]
        else:
            tags = ''

        metaDate = response.css('.header-content .date::text').re(
            r'([0-9]{,2}\/[0-9]{,2}\/[0-9]{4}, [0-9]{,2}:[0-9]{,2})')
        if len(metaDate) > 0:
            date = datetime.datetime.strptime(metaDate[0], '%d/%m/%Y, %H:%M')
        else:
            date = ''

        a = {
            'source': 'VNExpress',
            'url': response.url,
            'title': extract_with_css('.title-detail::text'),
            'sapo': extract_with_css('.description::text'),
            'body': ''.join(response.css('.Normal::text').getall()[:-2]).strip(),
            'cates': response.css(
                '.header-content.width_common > ul > li a::text').getall(),
            'tags': tags,
            'publish': date
        }
        print(a)
        return a
