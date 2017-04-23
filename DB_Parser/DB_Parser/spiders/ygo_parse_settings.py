monster_card_settings = {
    'name': '//*[@id="broad_title"]/div/h1/text()',
    'attribute': '//*[@id="details"]/tr[1]/td[1]/div/span[@class="item_box_value"]/text()',
    'level_rank': '//*[@id="details"]/tr[1]/td[2]/div/span[@class="item_box_value"]/text()',
    'monster_type': '//*[@id="details"]/tr[2]/td/div/text()',
    'monster_card_type': '//*[@id="details"]/tr[3]/td/div/text()',
    'attack': '//*[@id="details"]/tr[4]/td[1]/div/span[@class="item_box_value"]/text()',
    'defence': '//*[@id="details"]/tr[4]/td[2]/div/span[@class="item_box_value"]/text()',
    'card_description': '//*[@id="details"]/tr[5]/td/div/node()[not(self::div)]',
}


pendulum_card_settings = {
    'name': '//*[@id="broad_title"]/div/h1/text()',
    'attribute': '//*[@id="details"]/tr[1]/td[1]/div/span[@class="item_box_value"]/text()',
    'level_rank': '//*[@id="details"]/tr[1]/td[2]/div/span[@class="item_box_value"]/text()',
    'pendulum_scale': '//*[@id="details"]/tr[2]/td/div/text()',
    'pendulum_effect': '//*[@id="details"]/tr[3]/td/div/text()',
    'monster_type': '//*[@id="details"]/tr[4]/td/div/text()',
    'monster_card_type': '//*[@id="details"]/tr[5]/td/div/text()',
    'attack': '//*[@id="details"]/tr[6]/td[1]/div/span[@class="item_box_value"]/text()',
    'defence': '//*[@id="details"]/tr[6]/td[2]/div/span[@class="item_box_value"]/text()',
    'card_description': '//*[@id="details"]/tr[5]/td/div/node()[not(self::div)]',
}


magic_card_settings = {
    'name': '//*[@id="broad_title"]/div/h1/text()',
    'card_description': '//*[@id="details"]/tr[2]/td/div/node()[not(self::div)]',
    'card_type': '//*[@id="details"]/tr[1]/td/div/text()',
}
