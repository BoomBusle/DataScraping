import json
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class HotlineScraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.products = []

    def scrape_category(self, url):
        self.driver.get(url)
        time.sleep(3)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        try:
            product_elements = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".list-item--row")))
        except Exception as e:
            print(f"❌ Час очікування минув, елементи не завантажені: {e}")
            self.driver.quit()
            return

        for product in product_elements:
            try:
                name_element = product.find_element(By.CSS_SELECTOR, "div.list-item__title-container a")
                name = name_element.get_attribute('innerText').strip()
                link = name_element.get_attribute("href")
                price_range = product.find_element(By.CSS_SELECTOR, ".list-item__value-price").text.strip()
                try:
                    shop_count_text = product.find_element(By.CSS_SELECTOR, "a.link--black.text-sm.m_b-5").text                
                    shop_count = int(shop_count_text.split("(")[1].split(")")[0]) if "(" in shop_count_text else 1
                except:
                    shop_count = 1

                self.products.append({
                    "name": name,
                    "link": link,
                    "price_range": price_range,
                    "shop_count": shop_count,
                    "shops": []
                })
            except Exception as e:
                print(f"❌ Помилка при парсингу товару: {e}")

    def scrape_product(self, product):
        self.driver.get(product["link"])
        time.sleep(3)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        try:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".list__item")))
            shop_rows = self.driver.find_elements(By.CSS_SELECTOR, ".list__item")
            shops = []

            for shop in shop_rows:
                try:
                    shop_name = shop.find_element(By.CSS_SELECTOR, ".shop__title").text.strip()
                    price = shop.find_element(By.CSS_SELECTOR, ".price-block__price>.price-values").text.strip()
                    shops.append({"shop_name": shop_name, "price": price})                 
                except Exception:
                    continue

            product["shops"] = [shop for shop in shops if shop["shop_name"] and shop["price"]]
        except Exception as e:
            print(f"⚠️ Помилка при парсингу магазинів для {product['name']}: {e}")

    def save_to_json(self, filename="hotline_data.json"):
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(self.products, file, ensure_ascii=False, indent=4)

    def save_filtered_json(self, filename="hotline_filtered.json"):
        filtered_products = [product for product in self.products if product["shop_count"] >= 10]
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(filtered_products, file, ensure_ascii=False, indent=4)

    def run(self, category_url):
        print("🔍 Починаємо парсинг категорії...")
        self.scrape_category(category_url)

        print(f"📦 Знайдено {len(self.products)} товарів. Парсимо магазини...")
        for i, product in enumerate(self.products):
            print(f"➡️ ({i+1}/{len(self.products)}) {product['name']}...")
            self.scrape_product(product)

        print("💾 Збереження у JSON...")
        self.save_to_json()
        self.save_filtered_json() 
        print("✅ Готово! Дані в hotline_data.json та hotline_filtered.json")

        self.driver.quit()

if __name__ == "__main__":
    scraper = HotlineScraper()
    scraper.run("https://hotline.ua/ua/bt/kuhonnye-plity-i-poverhnosti/?p=25")