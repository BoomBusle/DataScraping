import scrapy

class NewsItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    date = scrapy.Field()
    img_url = scrapy.Field()
    image = scrapy.Field()
    img_name = scrapy.Field()