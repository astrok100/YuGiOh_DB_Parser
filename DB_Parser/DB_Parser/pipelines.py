# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import warnings
from sqlalchemy.orm import sessionmaker
from DB_Parser.database.models import *

class BasePipeline(object):

    def clean_item(self, item):
        meta_data = item.pop('card_meta_data', None)
        meta_data = [{ k: ''.join(v).strip() for k, v in data.items()} for data in meta_data]
        item = { k: ''.join(v).strip() for k, v in item.items()}
        item['card_meta_data'] = meta_data
        return item

class JSONPipeline(BasePipeline):

    def open_spider(self, spider):
        self.file = open('items.jl', 'wb')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        item = self.clean_item(item)
        line = json.dumps(item) + "\n"
        self.file.write(line)
        return item


class DBPipeline(BasePipeline):

    def open_spider(self, spider):
        create_deals_table(db_connect())
        self.session = sessionmaker(bind=db_connect())()
        self.rarity = {}
        self.card_type = {}
        self.monster_type = {}
        self.monster_card_type = {}
        self.monster_attribute = {}

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        with warnings.catch_warnings():
            warnings.filterwarnings('error')
            try:
                item = self.clean_item(item)
                self.add_to_db(item)
            except Warning as e:
                print item
                print e
            except Exception as e:
                print item
                print e
                self.session.rollback()
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
            
            meta['rarity'] =  meta['rarity'] if meta['rarity'] else "Normal"
            rarity = self.upsert(self.rarity, meta['rarity'], Rarity)

            meta_data = CardMetaData()
            meta_data.print_date = meta['print_date'] if meta['print_date'] else None
            meta_data.print_id = meta['print_id']
            meta_data.pack = meta['pack']
            meta_data.rarity = rarity
            meta_data.card = card
            self.session.add(meta_data)

            card.card_meta_data.append(meta_data)


        if item['card_type'].lower() == 'monster':
            monster = Monster()
            monster_type = self.upsert(
                self.monster_type, item['monster_type'], MonsterType)
            monster.monster_type = monster_type

            monster_attribute = self.upsert(self.monster_attribute, item['attribute'], MonsterAttribute)
            monster.monster_attribute = monster_attribute
            monster.pendulum_scale = item.get('pendulum_scale')
            monster.pendulum_effect = item.get('pendulum_effect')
            for m_card_type in item['monster_card_type'].split('/'):
                if m_card_type:
                    m_c_t = self.upsert(self.monster_card_type, m_card_type, MonsterCardType)
                    monster_card_type_group = MonsterCardTypeGroup()
                    monster_card_type_group.monster_card_type = m_c_t
                    monster.monster_card_type_group.append(monster_card_type_group)
            
            monster.level_rank = item['level_rank']
            monster.attack = item['attack']
            monster.defence = item['defence']
            monster.card = card
            self.session.add(monster)

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
