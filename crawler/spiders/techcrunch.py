# -*- coding: utf-8 -*-
import datetime

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import codecs
# from scrapy.selector import HtmlXPathSelector
# from scrapy.http.request import Request
#
# from crawler.items import CrawlerItem
# from crawler.utils import get_first

class FazSpider(CrawlSpider):
    name = 'techcrunch'
    rotate_user_agent = True
    allowed_domains = ['techcrunch.cn']
    start_urls = ['http://techcrunch.cn/']
    '''
    http://techcrunch.cn/mobile/page/12/
    http://techcrunch.cn/tag/instagram/
    http://techcrunch.cn/2015/05/01/twitters-new-dedicated-food-account-could-help-broaden-appeal/
    '''
    rules = (
        Rule(
            LinkExtractor(
                allow=(
                    r'techcrunch\.cn\/(\w+\/)+$',
                ),
                deny=(
                    r'techcrunch\.cn\/\d{4}\/\d{2}\/\d{2}\/',
                ),
            ),
            follow=True
        ),
        Rule(
            LinkExtractor(
                allow=(r'techcrunch\.cn\/\d{4}\/\d{2}\/\d{2}\/'),
                deny=(
                    r'techcrunch\.cn\/(\w+\/)+$',
                ),
            ),
            follow=True,
            callback='parse_page',
        ),
    )

    def parse_page(self, response):
        print(response.url)
        with codecs.open('urlList.txt', 'ab', 'utf-8') as file:
            file.write(response.url + '\n')
        # item = CrawlerItem()
        # item['url'] = response.url.encode('utf-8')
        # item['visited'] = datetime.datetime.now().isoformat().encode('utf-8')
        # item['published'] = get_first(response.selector.xpath('//span[@class="Datum"]/@content').extract())
        # item['title'] = get_first(response.selector.xpath('//meta[@property="og:title"]/@content').extract())
        # item['description'] = get_first(response.selector.xpath('//meta[@property="og:description"]/@content').extract()).strip()
        # item['text'] = "".join([s.strip().encode('utf-8') for s in response.selector.xpath('//div[@class="FAZArtikelText"]/div/p/text()').extract()])
        # item['author'] = [s.encode('utf-8') for s in response.selector.xpath('//span[@class="Autor"]/span[@class="caps last"]/a/span/text()').extract()]
        # item['keywords'] = [s.encode('utf-8') for s in response.selector.xpath('//meta[@name="keywords"]/@content').extract()]
        # return item
