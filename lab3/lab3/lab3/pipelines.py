import psycopg2
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from itemadapter import ItemAdapter
import re

class DataCleaningPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        for field in ["ПІБ", "Посада", "Email", "Телефон"]:
            if adapter.get(field):
                adapter[field] = adapter[field].strip()
        
        if adapter.get("Email") and not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", adapter["Email"]):
            adapter["Email"] = "Немає пошти"
        
        if adapter.get("Телефон") and not re.match(r"\(?\d{3,4}\)?[-.\s]?\d{2,3}[-.\s]?\d{2}[-.\s]?\d{2,4}", adapter["Телефон"]):
            adapter["Телефон"] = "Немає телефону"
        
        return item

class ImageDownloadPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if 'image_url' in item:
            yield scrapy.Request(item['image_url'])
    
    def file_path(self, request, response=None, info=None, *, item=None):
        name = item['ПІБ'].replace(" ", "_")
        return f"images/{name}.jpg"
    
    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        item['image_path'] = image_paths[0] if image_paths else None
        return item


class PostgresPipeline:
    def open_spider(self, spider):
        try:
            self.conn = psycopg2.connect(
                host='localhost',
                dbname='postgres',
                user='postgres',
                password='admin',
                port=5432
            )
            self.conn.autocommit = True
            self.cur = self.conn.cursor()
            
            self.cur.execute("SELECT 1 FROM pg_database WHERE datname='lab3_db'")
            if not self.cur.fetchone():
                self.cur.execute("CREATE DATABASE lab3_db")
                spider.logger.info("База даних 'lab3_db' створена")
            
            self.conn.close()
            self.conn = psycopg2.connect(
                host='localhost',
                dbname='lab3_db',
                user='postgres',
                password='admin',
                port=5432
            )
            self.cur = self.conn.cursor()
            
            self.cur.execute('''
                CREATE TABLE IF NOT EXISTS persons (
                    id SERIAL PRIMARY KEY,
                    pib TEXT NOT NULL,
                    position TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    page_url TEXT NOT NULL,
                    image_path TEXT
                )
            ''')
            self.conn.commit()
            
        except psycopg2.Error as e:
            spider.logger.error(f"PostgreSQL connection error: {e}")
            self.conn = None
            self.cur = None  
        
    def process_item(self, item, spider):
        if self.cur is None:
            return item  
        
        if 'image_url' in item and 'image_path' not in item:
            spider.logger.warning(f"Зображення ще не оброблено для {item.get('ПІБ')}")
            return item  
        
        self.cur.execute('''
            INSERT INTO persons (pib, position, email, phone, page_url, image_path)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (
            item.get("ПІБ"),
            item.get("Посада"),
            item.get("Email"),
            item.get("Телефон"),
            item.get("Сторінка"),
            item.get("image_path")
        ))
        self.conn.commit()
        return item

    def close_spider(self, spider):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()