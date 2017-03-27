# -*- coding: utf-8 -*-

from scrapy import Item, Field

class CardMetaDataItem(Item):
	rarity = Field()
	print_id = Field()
	pack = Field()
	print_date = Field()

class CardItem(Item):
    name = Field()
    card_description = Field()
    yugioh_cid = Field()
    card_type = Field()
    attribute = Field()
    level_rank = Field()
    attack = Field()
    defence = Field()
    pendulum_scale = Field()
    pendulum_effect = Field()
    monster_card_type = Field()
    monster_type = Field()
    card_meta_data = Field()