import re
from urlparse import urlsplit, parse_qs
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule
from DB_Parser.ygo_link_extractor import YGOLinkExtractor, LinkExtractor
from DB_Parser.items import CardItem, CardMetaDataItem
from DB_Parser.spiders.ygo_parse_settings import  (
    monster_card_settings, pendulum_card_settings, magic_card_settings)

class YGOSpider(CrawlSpider):
    name = "YGO"
    allowed_domains = ["db.yugioh-card.com"]

    url = 'https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=1&sort=1&rp=100&page={}'

    start_urls = [
        url.format(1),
    ]

    def process_next_page(value, attrs):
        # >> = \xbb
        if attrs.get('text_content') == u'\xbb':
            pattern = re.compile(r'javascript:ChangePage\((\d+)\)')
            m =  pattern.search(value)
            if m:
                print YGOCardExtractor.url.format(
                    m.group(1))
                return YGOCardExtractor.url.format(
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
            YGOLinkExtractor(
                allow=(r'card_search\.action\?ope=1&sort=1&rp=100&page='),
                process_value=process_next_page,
                restrict_css='div[class=page_num] span a',
                attrs=('href'),
                tags='a'
            ),
            follow=True
        )
    ]

    def parse_card(self, response):

        card_settings = self.get_parsing_settings(response)
        card = self.load_card_item(response, card_settings)
        return card

    def get_parsing_settings(self, response):

        title_paths = [
            # monster card
            '//*[@id="details"]/tr[2]/td/div/span/b/text()',
            # magic card
            '//*[@id="details"]/tr[1]/td/div/span/b/text()'
        ]

        title_type = {
            'icon': magic_card_settings,
            'pendulum scale': pendulum_card_settings,
            'monster type': monster_card_settings
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
        cgi = parse_qs(urlsplit(response.url).query)
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
