# -*- coding: utf-8 -*-

from scrapy import Item, Field

class CardMetaDataItem(Item):
	rarity = Field()
	print_id = Field()
	pack = Field()
	print_date = Field()

class CardItem(Item):
    name = Field()
    attribute = Field()
    level_rank = Field()
    monster_type = Field()
    monster_card_type = Field()
    attack = Field()
    defence = Field()
    card_description = Field()
    pendulum_scale = Field()
    pendulum_effect = Field()
    card_type = Field()
    yugioh_cid = Field()
    card_meta_data = Field()