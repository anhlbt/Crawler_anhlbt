# from newsplease import NewsPlease
# # article = NewsPlease.from_url('https://plo.vn/an-ninh-trat-tu/30-hoc-sinh-lop-12-di-chup-ky-yeu-gao-thet-trong-o-to-bi-lat-920059.html')
# article = NewsPlease.from_url('https://www.nytimes.com/2017/02/23/us/politics/cpac-stephen-bannon-reince-priebus.html?hp')

# print(article.title)


from newspaper import Article

url = 'https://vnexpress.net/evn-lap-doan-kiem-tra-xac-minh-tien-dien-tang-vot-4119709.html'
article = Article(url, language='vi')
article.download()
article.parse()
print("")


#==> news-pleases, newspaper3k not good in vietnamese