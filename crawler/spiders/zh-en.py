# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import CrawlSpider
import codecs
import os
import os.path
import re

class FazSpider(CrawlSpider):
    name = 'zh-en'
    def __init__(self):
        with codecs.open('cn_detail_url.txt', 'rb', 'utf-8') as file:
            self.urls = []
            for line in file.readlines():
                if '%' not in line:
                    self.url = line.strip()
                    self.urls.append(self.url)
                else:
                    pass
        self.headers = {
            'Host': 'techcrunch.cn',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.google.com/',
        }
        self.handle_httpstatus_list = [404, 500, 502, 503, 504, 400, 408]

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url, headers=self.headers, callback=self.parse_zh)

    def parse_zh(self, response):
        article_name = response.url.split('/')[-2]
        print('%s》》》》中文文章' % article_name)
        title = response.xpath('//title/text()').extract()[0].encode('utf-8').decode('utf-8')
        text = ''.join([s.encode('utf-8').decode('utf-8') for s in response.xpath('//div[@class="article-entry text"]//text()').extract()])
        save_folder = "./download/%s/" % article_name
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        article_doc = '%s.zh' % article_name
        article_path = os.path.join(save_folder, article_doc)
        with codecs.open(article_path, 'wb', 'utf-8') as file:
            file.writelines(title + text)

        url_en = 'https://techcrunch.com/%s/' % article_name
        headers = {
            'Host': 'techcrunch.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.google.com/',
        }
        # 这里发送请求，但是有可能响应404
        request = scrapy.FormRequest(url_en, headers=headers, callback=self.parse_en)
        request.meta['article_name'] = article_name
        return request

    def parse_en(self, response):
        # print('第一次英文url：' + response.url)
        article_name = response.meta['article_name']
        if response.status not in self.handle_httpstatus_list:
            print('%s》》》》状态码正确，直接解析' % article_name)
            title = response.xpath('//title/text()').extract()[0].encode('utf-8').decode('utf-8')
            text = ''.join([s.encode('utf-8').decode('utf-8') for s in response.xpath('//div[@class="article-entry text"]//text()').extract()])
            save_folder = "./download/%s/" % article_name
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)
            article_doc = '%s.en' % article_name
            article_path = os.path.join(save_folder, article_doc)
            with codecs.open(article_path, 'wb', 'utf-8') as file:
                file.writelines(title + text)
        else:
            # 如果返回404，就去搜索
            # https://techcrunch.com/sean-parkers-cancer-institute-may-have-found-a-blood-test-to-see-if-patients-will-respond-to-treatment/
            print('%s》》》》返回错误状态码，去搜索' % article_name)
            # search_url = 'https://techcrunch.com/search/%s#stq=%s&stp=1' % (article_name, article_name)
            # search_url = 'https://techcrunch.com/search/%s' % article_name
            search_url = r'https://api.swiftype.com/api/v1/public/engines/search.json?callback=jQuery1124049718058086000383_1492312830897&q={}&engine_key=zYD5B5-eXtZN9_epXvoo&page=1&per_page=10&facets%5Bpage%5D%5B%5D=author&facets%5Bpage%5D%5B%5D=category&facets%5Bpage%5D%5B%5D=tag&facets%5Bpage%5D%5B%5D=object_type&filters%5Bpage%5D%5Btimestamp%5D%5Btype%5D=range&spelling=always&_=1492312830898'.format(article_name)
            # print('request+++++++++++++++搜索url：' + search_url)
            headers = {
                'GET': search_url,
                'Host': 'api.swiftype.com',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'If-None-Match': 'W/"3599c41915e7d0abde1422b6e68188fd"',
                'Cache-Control': 'max-age=0',
            }
            request = scrapy.Request(search_url, headers=headers, callback=self.parse_search)
            request.meta['article_name'] = article_name
            return request

    def parse_search(self, response):
        # print('response==============搜索url：' + response.url)
        article_name = response.meta['article_name']
        reg = re.compile(r'"url":"(https://techcrunch\.com/\d{4}/\d{2}/\d{2}/[-\w]+/)"')
        if len(re.search(reg, response.body_as_unicode()).groups()) == 0:
            print('%s》》》》无搜索结果，放弃寻找此对应英文文章' % article_name)
            pass
        print('%s》》》》找到搜索结果并返回，待确认状态码是否正确' % article_name)
        article_url = re.search(reg, response.body_as_unicode()).group(1)
        # print('搜索出来的文章：' + article_url)
        headers = {
            'Host': 'techcrunch.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.google.com/',
        }
        request = scrapy.Request(article_url, headers=headers, callback=self.parse_en)
        request.meta['article_name'] = article_name
        return request





        # with codecs.open('xx.html', 'wb', 'utf-8') as file:
        #     file.writelines(response.body_as_unicode())
        # 返回json格式数据
        # "url": "https://techcrunch.com/2016/07/07/bumble-is-going-to-help-you-find-your-next-job-with-bumblebizz/",
        # body = response.body_as_unicode()[47:-2]
        # print(body)
        # json_body = json.loads(body)
        # print(json_body.keys())
        # 返回页面不包含要的内容
        # search_list = response.xpath("//h2[@class='post-title st-result-title']/a/@href").extract()
        # print(search_list)
        # if len(search_list) != 0:
        #     article_url = search_list[0]
        #     print('搜索出来的文章：' + article_url)
        #     headers = {
        #         'Host': 'techcrunch.com',
        #         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        #         'Accept-Language': 'zh-CN,zh;q=0.8',
        #         'Accept-Encoding': 'gzip, deflate, sdch, br',
        #         'Connection': 'keep-alive',
        #         'Upgrade-Insecure-Requests': '1',
        #         'Cache-Control': 'max-age=0',
        #         'Referer': 'https://www.google.com/',
        #     }
        #     yield scrapy.Request(article_url, headers=headers, callback=self.parse_en)
        # else:
        #     print('————————————无搜索结果——————————————')
        #     pass