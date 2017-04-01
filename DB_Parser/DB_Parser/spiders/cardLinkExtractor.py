import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class CardLinkExtractor(CrawlSpider):
    name = "cardlink"
    allowed_domains = ["db.yugioh-card.com"]
    start_urls = [
        'https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=1&sort=1&rp=10&page=1',
    ]

    def process_next_page(value):
        print value
        return "/javascript"

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
        # Rule(
        #     LinkExtractor(
        #         allow=('javascript'),
        #         process_value=process_next_page,
        #         restrict_css='div[class=page_num] span a'
        #     ),
        #     callback='parse_next_page'
        # )
    ]
    count =0
    def parse_card(self, response):
        self.count+=1
        print self.count
        print response.xpath('//*[@id="broad_title"]/div/h1/text()').extract()[0].strip()

    def parse_next_page(self, response):
        self.count+=1
        print self.count
