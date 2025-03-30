import scrapy
import re
from lab3.items import PersonItem

class CarpathiaCssSpider(scrapy.Spider):
    name = "carpathia_css"
    allowed_domains = ["carpathia.gov.ua"]
    start_urls = ["https://carpathia.gov.ua/persons"]

    def parse(self, response):
        people = response.css(".team_squad .col-sm-6 a")

        for person in people:
            name = person.css(".team-item_name::text").get(default="").strip()
            position = person.css(".team-item_employment::text").get(default="").strip()
            person_url = response.urljoin(person.attrib["href"])

            yield response.follow(
                person_url,
                self.parse_person,
                meta={"name": name, "position": position, "url": person_url}
            )

    def parse_person(self, response):
        item = PersonItem()
        item["ПІБ"] = response.meta["name"]
        item["Посада"] = response.meta["position"]
        item["Сторінка"] = response.meta["url"]
        item["Email"] = response.css(".card-info a[href^='mailto:']::text").get(default="Немає пошти")
        
        phone = None
        info_paragraphs = response.css(".card-info .main-text p::text").getall()
        for text in info_paragraphs:
            text = text.strip()
            phone_match = re.search(r"\(?\d{3,4}\)?[-.\s]?\d{2,3}[-.\s]?\d{2}[-.\s]?\d{2,4}", text)
            if phone_match:
                phone = phone_match.group()
        item["Телефон"] = phone or "Немає телефону"
        image_style = response.css(".team-item_photo::attr(style)").get()
        image_url = None
        if image_style:
            match = re.search(r'url\((.*?)\)', image_style)
            if match:
                image_url = response.urljoin(match.group(1).strip('"'))
            item["image_url"] = response.urljoin(image_url)

        yield item
