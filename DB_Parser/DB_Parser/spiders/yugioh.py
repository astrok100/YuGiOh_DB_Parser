import re
from urlparse import urlsplit, parse_qs
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule
from DB_Parser.yugioh_link_extractor import YuGiOhLinkExtractor, LinkExtractor
from DB_Parser.items import CardItem, CardMetaDataItem


class YuGiOhCardExtractor(CrawlSpider):
    name = "YuGiOh"
    allowed_domains = ["db.yugioh-card.com"]

    url = 'https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=1&sort=1&rp=10&page={}'

    start_urls = [
        url.format(1),
    ]

    monster_card_settings = {
        'name': '//*[@id="broad_title"]/div/h1/text()',
        'attribute': '//*[@id="details"]/tr[1]/td[1]/div/span[@class="item_box_value"]/text()',
        'level_rank': '//*[@id="details"]/tr[1]/td[2]/div/span[@class="item_box_value"]/text()',
        'monster_type': '//*[@id="details"]/tr[2]/td/div/text()',
        'monster_card_type': '//*[@id="details"]/tr[3]/td/div/text()',
        'attack': '//*[@id="details"]/tr[4]/td[1]/div/span[@class="item_box_value"]/text()',
        'defence': '//*[@id="details"]/tr[4]/td[2]/div/span[@class="item_box_value"]/text()',
        'card_description': '//*[@id="details"]/tr[5]/td/div/text()',
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
        'card_description': '//*[@id="details"]/tr[7]/td/div/text()',
    }


    magic_card_settings = {
        'name': '//*[@id="broad_title"]/div/h1/text()',
        'card_description': '//*[@id="details"]/tr[2]/td/div/text()',
        'card_type': '//*[@id="details"]/tr[1]/td/div/text()',
    }


    def process_next_page(value, attrs):
        # >> = \xbb
        if attrs.get('text_content') == u'\xbb':
            pattern = re.compile(r'javascript:ChangePage\((\d+)\)')
            m =  pattern.search(value)
            if m:
                return YuGiOhCardExtractor.url.format(
                    m.group(1))

    rules = [
        Rule(
            LinkExtractor(
                allow=(r'card_search.action.+cid.+'),
                tags='input',
                attrs='value',
                restrict_css='div[id=article_body] table'
            ),
            callback='parse_card',
            follow=True
        ),
        Rule(
            YuGiOhLinkExtractor(
                allow=(r'card_search\.action\?ope=1&sort=1&rp=10&page='),
                process_value=process_next_page,
                restrict_css='div[class=page_num] span a',
                attrs=('href'),
                tags='a'
            ),
            follow=False
        )
    ]

    def parse_card(self, response):

        card_settings = self.get_parsing_settings(response)
        card = self.load_card_item(response, card_settings)
        return card

    def get_parsing_settings(self, response):

        title_paths = [
            #monster card
            '//*[@id="details"]/tr[2]/td/div/span/b/text()',
            #magic card
            '//*[@id="details"]/tr[1]/td/div/span/b/text()'
        ]

        title_type = {
            'icon': self.magic_card_settings,
            'pendulum scale': self.pendulum_card_settings,
            'monster type': self.monster_card_settings
        }

        for title_path in title_paths:
            titles = response.xpath(title_path).extract()
            for title in titles:
                title = title.strip().lower()
                if title_type.get(title, None):
                    return (title, title_type.get(title))

    def load_card_item(self, response, card_settings):
        card_type, card_setting = card_settings
        item = ItemLoader(item=CardItem(), response=response)
        for key, xpath in card_setting.items():
            item.add_xpath(key, xpath)
        if card_type != 'icon':
            item.add_value('card_type', 'Monster')
        item.add_value('card_meta_data', self.meta_data(response))
        cgi = urlsplit(response.url).query
        cgi = parse_qs(cgi)
        item.add_value('yugioh_cid', cgi.get('cid'))
        card = item.load_item()
        return card

    def meta_data(self, response):
        meta_data_selector = '//*[@id="pack_list"]/table/tr[@class="row"]'
        meta_data = response.xpath(meta_data_selector)
        table_column = {
            "print_date": 'td[1]/text()',
            "print_id": 'td[2]/text()',
            "pack": 'td[3]/b/text()',
            "rarity": 'td[4]/img/@alt'
        }
        items = []
        for row in meta_data:
            item = CardMetaDataItem()
            for k, v in table_column.items():
                item[k]= row.xpath(v).extract()
            items.append(item)
        return items
