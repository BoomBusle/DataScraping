import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://carpathia.gov.ua"
LIST_URL = f"{BASE_URL}/persons"

response = requests.get(LIST_URL)
soup = BeautifulSoup(response.text, "html.parser")

print("HTML-код сторінки зі списком осіб:\n")
print(soup.prettify())  

people = soup.select(".team_squad .col-sm-6 a")

people_data = []

for person in people:
    name = person.select_one(".team-item_name").text.strip()
    position = person.select_one(".team-item_employment").text.strip()
    person_url = BASE_URL + person["href"]

    person_response = requests.get(person_url)
    person_soup = BeautifulSoup(person_response.text, "html.parser")

    email = None
    phone = None

    info_paragraphs = person_soup.select(".card-info .main-text p")

    for p in info_paragraphs:
        text = p.get_text(strip=True)

        text = re.sub(r"Функціональні обов'язки|E-mail:", "", text, flags=re.IGNORECASE).strip()

        if not email:
            email_tag = p.find("a", href=lambda href: href and "mailto:" in href)
            if email_tag:
                email = email_tag.text.strip()

        phone_match = re.search(r"\(?\d{3,4}\)?[-.\s]?\d{2,3}[-.\s]?\d{2}[-.\s]?\d{2}", text)
        if phone_match:
            phone = phone_match.group()

        if not email and "@" in text:
            parts = re.split(r"\s+", text)
            for part in parts:
                if "@" in part:
                    email = part.strip()
                elif re.search(r"\d", part):
                    phone = part.strip()

    people_data.append(f"ПІБ: {name or 'Немає ПІБ'}\nПосада: {position or 'Немає посади'}\nПошта: {email or 'Немає пошти'}\nНомер: {phone or 'Немає телефону'}\nСторінка: {person_url}\n" + "-" * 100)

with open("people_data.txt", "w", encoding="utf-8") as f:
    for entry in people_data:
        f.write(entry + "\n")

print("\nДані збережено у people_data.txt")
