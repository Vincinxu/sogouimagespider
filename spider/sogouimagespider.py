from requests.exceptions import ConnectionError
import requests
import os
import pymongo
from urllib.parse import urlencode
from hashlib import md5
from multiprocessing.pool import Pool

class SogouImageSpider():
    '''
    初始化
    '''
    def __init__(self, keyword, mongo_uri, mongo_db, mongo_collection):
        self.keyword = keyword
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection
        

    '''
    获取Ajax加载的数据
    '''
    def get_data(self, start):
        try:
            p = {
                'query': self.keyword,
                'mode': 1,
                'start': start,
                'reqType': 'ajax',
                'reqFrom': 'result',
                'tn': 0
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            }
            url = 'https://pic.sogou.com/pics?' + urlencode(p, encoding='GBK')
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            return None
        except ConnectionError:
            return None

    '''
    提取Ajax加载的数据，分别是title和image
    '''
    def parse_json(self, json):
        items = json.get('items')
        for item in items:
            product = {
                'title': item.get('title'),
                'image': item.get('pic_url')
            }
            yield product


    '''
    保存到mongoDB
    '''
    def save_to_mongodb(self, content):
        self.client = pymongo.MongoClient(self.mongo_uri)
        db = self.client[self.mongo_db]
        db[self.mongo_collection].insert(dict(content))

    '''
    关闭mongoDB
    '''
    def close_mongodb(self):
        self.client.close()

    '''
    下载图片到本地
    '''
    def save_to_image(self, item):
        if not os.path.exists('sogou'):
            os.mkdir('sogou')
        try:
            response = requests.get(item.get('image'))
            if response.status_code == 200:
                file_path = '%s/%s.jpg' % ('sogou', md5(response.content).hexdigest())
                if not os.path.exists(file_path):
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                        print(item)
        except:
            print('下载失败:', item.get('title'))

    '''
    组织爬虫运行流程
    '''
    def run(self, page):
        json = self.get_data(page)
        content = self.parse_json(json)
        for item in content:
            self.save_to_mongodb(item)
            self.save_to_image(item)
        self.close_mongodb()

'''
使用多进程启动运行
'''
if __name__ == '__main__':
    max_page = 2
    pool = Pool(3)
    groups = ([i * 48 for i in range(1, max_page + 1)])
    pool.map(SogouImageSpider('海贼王', 'localhost', 'sogou', 'one piece').run, groups)
    pool.close()
    pool.join()

