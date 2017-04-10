# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

class CardPipeline(object):

    def open_spider(self, spider):
        self.file = open('items.jl', 'wb')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        meta_data = item.pop('card_meta_data', None)
        meta_data = [{ k: ''.join(v).strip() for k, v in data.items()} for data in meta_data]
        item = { k: ''.join(v).strip() for k, v in item.items()}
        item['card_meta_data'] = meta_data
        line = json.dumps(item) + "\n"
        self.file.write(line) 
        return item