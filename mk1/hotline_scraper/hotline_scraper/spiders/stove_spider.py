import scrapy
import json

class StoveSpider(scrapy.Spider):
    name = "stove"
    start_urls = ["https://hotline.ua/ua/bt/kuhonnye-plity-i-poverhnosti/?p=25"]

    def parse(self, response):
        stoves = []
        for product in response.css("div.list-item"):
            name = product.css("a.item-title::text").get(default="").strip()
            link = response.urljoin(product.css("a.item-title::attr(href)").get(default=""))
            price_range = product.css("div.list-item__value-price::text").get(default="").strip()
            
            shop_count_text = product.css("a.link--black.text-sm.m_b-5::text").get(default="")
            shop_count = int(shop_count_text.split("(")[1].split(")")[0]) if "(" in shop_count_text else 0
            
            shops = []
            for shop in product.css("div.list div.list__item"):
                shop_name = shop.css("span.shop__title a::text").get(default="").strip()
                shop_link = response.urljoin(shop.css("span.shop__title a::attr(href)").get(default=""))
                shop_price = shop.css("span.price__value::text").get(default="").strip()
                
                if shop_name and shop_price:
                    shops.append(f"{shop_name} | {shop_link} | {shop_price}")

            stoves.append({
                "name": name,
                "link": link,
                "price_range": price_range,
                "shop_count": shop_count,
                "shops": shops
            })
        
        self.save_to_file("stoves.json", stoves)
        
        filtered_stoves = [stove for stove in stoves if stove["shop_count"] > 10]
        self.save_to_file("filtered_stoves.json", filtered_stoves)

    def save_to_file(self, filename, data):
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)