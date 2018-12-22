# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
import json
from urllib.request import urlretrieve


class WeiboPipeline(object):
    def open_spider(self, spider):
        self.f = open('data/url.json', 'w')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + ",\n"
        self.f.write(line)

    def close_spider(self, spider):
        self.f.close()


class ScaleImg(ImagesPipeline):
    def get_media_requests(self, item, info):
        yield scrapy.Request(url=item['url'])

    def item_completed(self, results, item, info):
        img_path = [x['path'] for ok, x in results if ok]
        if not img_path:
            raise DropItem("download fail-------------")
        return item


class DownImg(object):
    path = 'data/images/'    
    def process_item(self, item, spider):
        urlretrieve(item['url'], self.path + item['name'] + '.jpg')
