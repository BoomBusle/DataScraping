import scrapy
import re


class CarpathiaSpider(scrapy.Spider):
    name = "carpathia_xpath"
    allowed_domains = ["carpathia.gov.ua"]
    start_urls = ["https://carpathia.gov.ua/persons"]

    def parse(self, response):
        # Отримуємо список людей
        people = response.css(".team_squad .col-sm-6 a")

        for person in people:
            name = person.css(".team-item_name::text").get().strip()
            position = person.css(".team-item_employment::text").get().strip()
            person_url = response.urljoin(person.attrib["href"])

            yield response.follow(
                person_url,
                self.parse_person,
                meta={"name": name, "position": position, "url": person_url}
            )

    def parse_person(self, response):
        name = response.meta["name"]
        position = response.meta["position"]
        person_url = response.meta["url"]

        email = None
        phone = None

        info_paragraphs = response.xpath("//div[contains(@class, 'card-info')]//p/text()").getall()

        for text in info_paragraphs:
            text = text.strip()
            text = re.sub(r"Функціональні обов'язки|E-mail:", "", text, flags=re.IGNORECASE).strip()

            if not email and "@" in text:
                email = text

            phone_match = re.search(r"\(?\d{3,4}\)?[-.\s]?\d{2,3}[-.\s]?\d{2}[-.\s]?\d{2,4}", text)
            if phone_match:
                phone = phone_match.group()

        yield {
            "ПІБ": name,
            "Посада": position,
            "Email": email or "Немає пошти",
            "Телефон": phone or "Немає телефону",
            "Сторінка": person_url
        }
