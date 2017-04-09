import re
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from lxml import etree
from scrapy.linkextractors.lxmlhtml import LxmlParserLinkExtractor, _nons, _collect_string_content 
from scrapy.utils.misc import arg_to_iter, rel_has_nofollow
from scrapy.utils.python import unique as unique_list, to_native_str
from six.moves.urllib.parse import urlparse, urljoin
from scrapy.utils.response import get_base_url
from scrapy.link import Link
from DB_Parser.items import CardItem, CardMetaDataItem
from scrapy.loader import ItemLoader

class YuGiOhParserLink(LxmlParserLinkExtractor):
    def __init__(self, tag="a", attr="href", process=None, unique=False):

        super(YuGiOhParserLink, self).__init__(
            tag=tag, attr=attr, process=process, unique=unique
        )

    def _extract_links(self, selector, response_url, response_encoding, base_url):
        links = []
        # hacky way to get the underlying lxml parsed document
        for el, attr, attr_val in self._iter_links(selector.root):
            # pseudo lxml.html.HtmlElement.make_links_absolute(base_url)
            try:
                attr_val = urljoin(base_url, attr_val)

            except ValueError:
                continue # skipping bogus links
            else:
                url = self.process_attr(attr_val, el.attrib)
                if url is None:
                    continue
            url = to_native_str(url, encoding=response_encoding)
            # to fix relative links after process_value
            url = urljoin(response_url, url)
            link = Link(url, _collect_string_content(el) or u'',
                        nofollow=rel_has_nofollow(el.get('rel')))

            links.append(link)
        return self._deduplicate_if_needed(links)


class YuGiOhLinkExtractor(LinkExtractor):
    def __init__(self, allow=(), deny=(), allow_domains=(), deny_domains=(), restrict_xpaths=(),
                 tags=('a', 'area'), attrs=('href',), canonicalize=True,
                 unique=True, process_value=None, deny_extensions=None, restrict_css=()):
        self.tags = tags
        self.attrs = attrs
        tag_func = lambda x: x in set(arg_to_iter(self.tags))
        attr_func = lambda x: x in set(arg_to_iter(self.attrs))

        super(YuGiOhLinkExtractor, self).__init__(
            allow=allow, deny=deny,
            allow_domains=allow_domains, deny_domains=deny_domains,
            restrict_xpaths=restrict_xpaths, restrict_css=restrict_css,
            canonicalize=canonicalize, deny_extensions=deny_extensions
        )

        self.link_extractor = YuGiOhParserLink(
            tag=tag_func, attr=attr_func,
            unique=unique,
            process=process_value
        )


    def extract_links(self, response):
        base_url = get_base_url(response)
        if self.restrict_xpaths:
            docs = [subdoc
                    for x in self.restrict_xpaths
                    for subdoc in response.xpath(x)]
        else:
            docs = [response.selector]
        all_links = []
        for doc in docs:
            doc.root.attrib['text_content'] = doc.root.text_content()
            links = self._extract_links(doc, response.url, response.encoding, base_url)
            all_links.extend(self._process_links(links))
        return unique_list(all_links)

class CardLinkExtractor(CrawlSpider):
    name = "cardlink"
    allowed_domains = ["db.yugioh-card.com"]
    start_urls = [
        'https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=1&sort=1&rp=10&page=1',
    ]
    def process_next_page(value, attrs):
        if attrs.get('text_content') == u'\xbb':
            pattern = re.compile(r'javascript:ChangePage\((\d+)\)')
            m =  pattern.search(value)
            if m:
                return 'https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=1&sort=1&rp=10&page={}'.format(
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

        parse = self.get_parsing_function(response)
        item = parse(response)
        item.add_value('card_meta_data', self.meta_data(response))
        card = item.load_item()
        print "\n"
        for k, v in dict(card).items():
            self.log(k + ' : {}'.format(v))
        print "\n"
        

    def get_parsing_function(self, response):

        title_paths = ['//*[@id="details"]/tr[2]/td/div/span/b/text()', '//*[@id="details"]/tr[1]/td/div/span/b/text()']
        title_type = {
            'icon': self.parse_magic_trap,
            'pendulum scale': self.parse_pendulum,
            'monster type': self.parse_monster
        }

        for title_path in title_paths:
            titles = response.xpath(title_path).extract()
            for title in titles:
                title = title.strip().lower()
                if title_type.get(title, None):
                    return title_type.get(title)

    def parse_monster(self, response):
        item = ItemLoader(item=CardItem(), response=response)
        item.add_xpath('name', '//*[@id="broad_title"]/div/h1/text()')
        item.add_xpath('attribute', '//*[@id="details"]/tr[1]/td[1]/div/span[@class="item_box_value"]/text()')
        item.add_xpath('level_rank', '//*[@id="details"]/tr[1]/td[2]/div/span[@class="item_box_value"]/text()')
        item.add_xpath('monster_type', '//*[@id="details"]/tr[2]/td/div/text()')
        item.add_xpath('monster_card_type', '//*[@id="details"]/tr[3]/td/div/text()')
        item.add_xpath('attack', '//*[@id="details"]/tr[4]/td[1]/div/span[@class="item_box_value"]/text()')
        item.add_xpath('defence', '//*[@id="details"]/tr[4]/td[2]/div/span[@class="item_box_value"]/text()')
        item.add_xpath('card_description', '//*[@id="details"]/tr[5]/td/div/text()')
        item.add_value('card_type', 'Monster')
        return item

    def parse_magic_trap(self, response):

        item = ItemLoader(item=CardItem(), response=response)
        item.add_xpath('name', '//*[@id="broad_title"]/div/h1/text()')
        item.add_xpath('card_description', '//*[@id="details"]/tr[2]/td/div/text()')
        item.add_xpath('card_type', '//*[@id="details"]/tr[1]/td/div/text()')
        return item

    def parse_pendulum(self, response):
        item = ItemLoader(item=CardItem(), response=response)
        item.add_xpath('name', '//*[@id="broad_title"]/div/h1/text()')
        item.add_xpath('attribute', '//*[@id="details"]/tr[1]/td[1]/div/span[@class="item_box_value"]/text()')
        item.add_xpath('level_rank', '//*[@id="details"]/tr[1]/td[2]/div/span[@class="item_box_value"]/text()')
        item.add_xpath('pendulum_scale', '//*[@id="details"]/tr[2]/td/div/text()')
        item.add_xpath('pendulum_effect', '//*[@id="details"]/tr[3]/td/div/text()')
        item.add_xpath('monster_type', '//*[@id="details"]/tr[4]/td/div/text()')
        item.add_xpath('monster_card_type', '//*[@id="details"]/tr[5]/td/div/text()')
        item.add_xpath('attack', '//*[@id="details"]/tr[6]/td[1]/div/span[@class="item_box_value"]/text()')
        item.add_xpath('defence', '//*[@id="details"]/tr[6]/td[2]/div/span[@class="item_box_value"]/text()')
        item.add_xpath('card_description', '//*[@id="details"]/tr[7]/td/div/text()')
        item.add_value('card_type', 'Monster')
        return item

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
                item[k]= row.xpath(v).extract_first()
            items.append(item)
        return items
