import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re
from lxml import etree
from scrapy.linkextractors.lxmlhtml import LxmlParserLinkExtractor, _nons, _collect_string_content 
from scrapy.utils.misc import arg_to_iter, rel_has_nofollow
from scrapy.utils.python import unique as unique_list, to_native_str
from six.moves.urllib.parse import urlparse, urljoin
from scrapy.utils.response import get_base_url
from scrapy.link import Link

class YuGiOhParserLink(LxmlParserLinkExtractor):
    def __init__(self, tag="a", attr="href", process=None, unique=False):

        super(YuGiOhParserLink, self).__init__(
            tag=tag, attr=attr, process=process, unique=unique
        )
        # self.attr = attr
        # print attr
        # print "aaaaaaaaaaaa"
        # print (el.text_content() == u'\xbb'), el.values()

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
            print url
            link = Link(url, _collect_string_content(el) or u'',
                        nofollow=rel_has_nofollow(el.get('rel')))
            links.append(link)
        return self._deduplicate_if_needed(links)

class YuGiOhLinkExtractor(LinkExtractor):
    def __init__(self, *args, **kwargs):
        self.tags = kwargs.get('tags')
        self.attrs = kwargs.get('attrs')
        tag_func = lambda x: x in set(arg_to_iter(self.tags))
        attr_func = lambda x: x in set(arg_to_iter(self.attrs))
        super(YuGiOhLinkExtractor, self).__init__(
            *args, **kwargs
        )

        self.link_extractor = YuGiOhParserLink(
            tag=tag_func, attr=attr_func,
            unique=kwargs.get('unique'),
            process=kwargs.get('process_value')
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
                allow=('javascript'),
                process_value=process_next_page,
                restrict_css='div[class=page_num] span a',
                attrs=('href'),
                tags='a'
            ),
            follow=True
        )
    ]
    count =0
    def parse_card(self, response):
        self.count+=1
        print self.count
        print response.xpath('//*[@id="broad_title"]/div/h1/text()').extract()[0].strip()