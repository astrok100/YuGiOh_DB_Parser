# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from sqlalchemy.orm import sessionmaker
from DB_Parser.database.models import *

class CardPipeline(object):

    def open_spider(self, spider):
        create_deals_table(db_connect())
        self.session = sessionmaker(bind=db_connect())()
        self.file = open('items.jl', 'wb')
        self.rarity = {}
        self.card_type = {}
        self.monster_type = {}

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        meta_data = item.pop('card_meta_data', None)
        meta_data = [{ k: ''.join(v).strip() for k, v in data.items()} for data in meta_data]
        item = { k: ''.join(v).strip() for k, v in item.items()}
        item['card_meta_data'] = meta_data
        line = json.dumps(item) + "\n"
        self.file.write(line)
        self.add_to_db(item)
        return item

    def add_to_db(self, item):

        card_type = self.upsert(self.card_type, item['card_type'], CardType)

        card = Card()
        card.name = item['name']
        card.image = 'na'
        card.card_desc = item['card_description']
        card.yugioh_cid = item['yugioh_cid']
        card.card_type = card_type

        card.card_meta_data = []
        for meta in item['card_meta_data']:

            rarity = self.upsert(self.rarity, meta['rarity'], Rarity)

            meta_data = CardMetaData()
            meta_data.print_date = meta['print_date']
            meta_data.print_id = meta['print_id']
            meta_data.pack = meta['pack']
            meta_data.rarity = rarity
            meta_data.card = card
            self.session.add(meta_data)

            card.card_meta_data.append(meta_data)


        if item['card_type'].lower() == 'monster':
            monster_type = self.upsert(
                self.monster_type, item['monster_type'], MonsterType)
            for m_card_type in item['monster_card_type']:
                # monster_card_type should be an list fix it
                pass


        self.session.add(card)
        self.session.commit()


    def upsert(self, cache_dict, item_key, model):
        if cache_dict.get(item_key):
            cache_model = cache_dict.get(item_key)
        else:
            cache_model = model(item_key)
            cache_dict[item_key] = cache_model
            self.session.add(cache_model)
        return cache_model
