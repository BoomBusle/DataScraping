import scrapy
import re

class CarpathiaSpider(scrapy.Spider):
    name = "carpathia"
    start_urls = ["https://carpathia.gov.ua/persons"]

    def parse(self, response):
        people_links = response.css(".team_squad .col-sm-6 a::attr(href)").getall()
        for link in people_links:
            full_url = response.urljoin(link)
            yield scrapy.Request(full_url, callback=self.parse_person)

    def parse_person(self, response):
        name = response.css(".page-title-text::text").get(default="").strip()
        position = response.css(".team-item_employment::text").get(default="").strip()
        email = None
        phone = None

        info_paragraphs = response.css(".card-info .main-text p")

        for p in info_paragraphs:
            text = p.get()

            text = re.sub(r"Функціональні обов'язки|E-mail:", "", text, flags=re.IGNORECASE).strip()

            email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
            if email_match:
                email = email_match.group()

            phone_match = re.search(r"\(?\d{3,4}\)?[-.\s]?\d{2,3}[-.\s]?\d{2}[-.\s]?\d{2}", text)
            if phone_match:
                phone = phone_match.group()

        yield {
            "ПІБ": name,
            "Посада": position,
            "Email": email or "Немає email",
            "Телефон": phone or "Немає телефону",
            "Сторінка": response.url
        }
