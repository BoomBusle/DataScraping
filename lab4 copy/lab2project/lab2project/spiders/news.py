import scrapy
from bs4 import BeautifulSoup
from lab2project.items import NewsItem
import requests


class NewsSpider(scrapy.Spider):
    name = "news"
    allowed_domains = ["radiosvoboda.org"]
    start_urls = ["https://www.radiosvoboda.org/z/630"]

    def parse(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        count = 1
        items = soup.find_all('div', class_='media-block')
        for item in items:
            print(count)
            count += 1
            title = item.find('h4').text.strip()
            url = item.find('a')['href']
            date = item.find('span').text.strip()
            img_url = item.find('img')['src']
            img_name = f"img+{date}"

            data = {
                "title": title,
                "url": url,
                "date": date,
                "img_url": img_url,
                "img_name": img_name
            }

            try:
                response = requests.post("http://localhost:3001/news", json=data)
                print(f"Відправлено: {response.status_code} -> {title}")
            except Exception as e:
                print(f"Помилка надсилання: {e}")

            yield NewsItem(**data)
