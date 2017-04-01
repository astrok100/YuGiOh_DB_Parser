import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class CardLinkExtractor(CrawlSpider):
    name = "cardlink"
    allowed_domains = ["db.yugioh-card.com"]
    start_urls = [
        'https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=1&sort=1&rp=100&page=1',
    ]
    rules = [
        # Rule(
        #     LxmlLinkExtractor(
        #         allow=(r'card_search.action.+cid.+'),
        #         tags='input',
        #         attrs='value'
        #     ),
        #     callback='parse_card'
        # ),
        Rule(
            LxmlLinkExtractor(
                allow=(r'javascript\:Change'),
                # process_value='process_next_page'
            ),
            callback='parse_next_page'
        )
    ]
    count =0
    def parse_card(self, response):
        self.count+=1
        print self.count
        print response

    def parse_next_page(self, response):
        print "hello"

    def process_next_page(self, value):
        print "HMPTPTPTPTPTPTPTPPPPPPPP"
        print value
        return value