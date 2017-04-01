# -*- coding: utf-8 -*-

from scrapy.http import Request
from scrapy import Spider
from DB_Parser.items import CardItem, CardMetaDataItem
from scrapy.loader import ItemLoader
from BeautifulSoup import BeautifulSoup
from scrapy.http import HtmlResponse

def NextURL():
    """
    Generate a list of URLs to crawl. You can query a database or come up with some other means
    Note that if you generate URLs to crawl from a scraped URL then you're better of using a 
    LinkExtractor instead: http://doc.scrapy.org/topics/link-extractors.html
    """
    list_of_urls = [ 
        "https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=2&cid=" + str(i)
        for i in range(12714, 12715)
    ]
    
    for next_url in list_of_urls:
        yield next_url


class YugiohSpider(Spider):
    name = "yugioh"
    allowed_domains = ["db.yugioh-card.com"]

    url = NextURL()
    
    start_urls = []
    
    def start_requests(self):
        """
        NOTE: This method is ONLY CALLED ONCE by Scrapy (to kick things off).
        Get the first url to crawl and return a Request object
        This will be parsed to self.parse which will continue
        the process of parsing all the other generated URLs
        """

        ## grab the first URL to being crawling
        start_url = self.url.next()
        
        self.log('START_REQUESTS : start_url = %s' % start_url)

        request = Request(start_url, dont_filter=True)
        
        ### important to yield, not return (not sure why return doesn't work here)
        yield request
    
    def parse(self, response):
        """
        Parse the current response object, and return any Item and/or Request objects
        """
        self.log("SCRAPING '%s'" % response.url)
        self.log(response.xpath('//*[@id="article_body"]/div/text()').extract_first().strip())
        card = None
        if not (response.xpath('//*[@id="article_body"]/div/text()').extract_first().strip() == 'No Data Found.'):
            item = ItemLoader(item=CardItem(), response=response)
            item.add_xpath('name', '//*[@id="broad_title"]/div/h1/text()')
            item.add_xpath('card_description', '//*[@id="details"]/tr[5]/td/div')
            item.add_xpath('card_type', '//*[@id="details"]/tr[3]/td/div')
            item.add_xpath('attribute', '//*[@id="details"]/tr[1]/td[1]/div/span[2]/text()')
            item.add_xpath('level_rank', '//*[@id="details"]/tr[1]/td[2]/div/span[2]/text()')
            item.add_xpath('attack', '//*[@id="details"]/tr[4]/td[1]/div/span[2]/text()')
            item.add_xpath('defence', '//*[@id="details"]/tr[4]/td[2]/div/span[2]/text()')
            item.add_xpath('pendulum_scale', '//*[@id="details"]/tr[2]/td/div/text()')
            item.add_xpath('pendulum_effect', '//*[@id="details"]/tr[3]/td/div/text()')
            item.add_xpath('monster_card_type', '//*[@id="details"]/tr[3]/td/div/text()')
            item.add_xpath('monster_type', '//*[@id="details"]/tr[2]/td/div/text()')
            # item.add_xpath('card_meta_data', '//*[@id="broad_title"]/div/h1/text()')
            card = item.load_item()
            for k, v in dict(card).items():
                self.log(k + ' : {}'.format(v))
        ## extract your data and yield as an Item (or DjangoItem if you're using django-celery)

        ## get the next URL to crawl
        next_url = self.url.next()
        yield Request(next_url)
    ##parse()
