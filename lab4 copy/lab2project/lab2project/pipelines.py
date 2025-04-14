# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class Lab2ProjectPipeline:
    def process_item(self, item, spider):
        return item

class ImagePipeline:
    def process_item(self, item, spider):
        if 'img_url' in item:
            img_url = item['img_url']
            img_name = img_url.split('/')[-1]
            response = requests.get(img_url)
            if response.status_code == 200:
                os.makedirs('images', exist_ok=True)
                img_path = os.path.join('images', img_name)
                with open(img_path, 'wb') as f:
                    f.write(response.content)
            else:
                spider.logger.error(f"Не вдалося завантажити фото: {img_url}")
        return item
    

class DBPipeline:
    def open_spider(self, spider):
        try:
            self.conn = sqlite3.connect('news.db')
            self.cursor = self.conn.cursor()
            spider.logger.info(" Відкрито з'єднання з БД")
        
            self.cursor.execute(
                '''CREATE TABLE IF NOT EXISTS news 
                (title TEXT, url TEXT, date TEXT, img_url TEXT, img_name TEXT, image BLOB)'''
                )
            self.conn.commit()
            spider.logger.info(" Таблиця 'news' перевірена/створена")
        except Exception as e:
            spider.logger.error(f" Помилка відкриття БД: {e}")

    

    def process_item(self, item, spider):
        try:
            img_data = None
            if 'img_url' in item and item['img_url']:  
                response = requests.get(item['img_url'])
                if response.status_code == 200:
                    img_data = response.content
            
            self.cursor.execute(
                '''INSERT INTO news (title, url, date, img_url, img_name, image) 
                VALUES (?, ?, ?, ?, ?, ?)''', 
                (item['title'], item['url'], item['date'], item.get('img_url', None), item.get('img_name', None), img_data)
            )
            self.conn.commit()
        except Exception as e:
            spider.logger.error(f"Error inserting data into database: {e}")
        return item
    def close_spider(self, spider):
        if self.conn:
            self.conn.close()
