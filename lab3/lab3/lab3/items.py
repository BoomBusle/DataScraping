import scrapy

class PersonItem(scrapy.Item):
    ПІБ = scrapy.Field()
    Посада = scrapy.Field()
    Email = scrapy.Field()
    Телефон = scrapy.Field()
    Сторінка = scrapy.Field()
    image_url = scrapy.Field()
    image_path = scrapy.Field()
