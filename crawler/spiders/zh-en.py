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
        # 读取中文文章url
        with codecs.open('cn_detail_url.txt', 'rb', 'utf-8') as file:
            self.urls = []
            for line in file.readlines():
                # 有中文的链接先不做处理
                if '%' in line:
                    with codecs.open('zh_have.txt', 'ab', 'utf-8') as file:
                        file.writelines(line + '\n')
                    pass
                else:
                    self.url = line.strip()
                    self.urls.append(self.url)
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
        self.handle_httpstatus_list = [404, 500, 502, 503, 504, 400, 408, 520]

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url, headers=self.headers, callback=self.parse_zh)

    def parse_zh(self, response):
        article_name = response.url.split('/')[-2]
        print('%s 》》》》中文文章 》》》%s' % (article_name, response.url))
        title = response.xpath('//title/text()').extract()[0].strip().encode('utf-8').decode('utf-8')
        text = ''.join([s.strip().encode('utf-8').decode('utf-8') for s in response.xpath('//div[@class="article-entry text"]//p//text()').extract()])
        with codecs.open('zh.zh', 'ab', 'utf-8') as file:
            file.writelines(title + '\n' + text)

        # save_folder = "./download/%s/" % article_name
        # if not os.path.exists(save_folder):
        #     os.makedirs(save_folder)
        # article_doc = '%s.zh' % article_name
        # article_path = os.path.join(save_folder, article_doc)
        # with codecs.open(article_path, 'wb', 'utf-8') as file:
        #     file.writelines(title + text)
        # url = os.path.join(save_folder, 'url.txt')
        # with codecs.open(url, 'wb', 'utf-8') as file:
        #     file.writelines(response.url)

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
        # 直接在底部寻找原文链接，找到直接获取，未找到则直接跳转
        url_ens = response.xpath('//div[@class="article-entry text"]//p//a/@href').extract()
        if len(url_ens) != 0:
            url_en = url_ens[0]
        else:
            url_en = 'https://techcrunch.com/%s/' % article_name
        # 这里发送请求，但是有可能响应404或其他状态码
        request = scrapy.Request(url_en, headers=headers, callback=self.parse_en)
        request.meta['article_name'] = article_name
        return request

    def parse_en(self, response):
        article_name = response.meta['article_name']
        if response.status == 200:
            print('%s》》》》状态码正确，直接解析' % article_name)
            title = response.xpath('//title/text()').extract()[0].strip().encode('utf-8').decode('utf-8')
            text = ''.join([s.strip().encode('utf-8').decode('utf-8') for s in response.xpath('//div[@class="article-entry text"]//p//text()').extract()])
            with codecs.open('en.en', 'ab', 'utf-8') as file:
                file.writelines(title + '\n' + text)
        else:
            # 如果返回错误状态码，记录
            print('%s 》》》》状态码错误，记录 》》》》%s' % (article_name, response.url))
            with codecs.open('wrong_status.txt', 'ab', 'utf-8') as file:
                file.writelines(response.url + '\n')


    #
    #
    #         # search_url = 'https://techcrunch.com/search/%s#stq=%s&stp=1' % (article_name, article_name)
    #         # search_url = 'https://techcrunch.com/search/%s' % article_name
    #         search_url = r'https://api.swiftype.com/api/v1/public/engines/search.json?callback=jQuery1124049718058086000383_1492312830897&q={}&engine_key=zYD5B5-eXtZN9_epXvoo&page=1&per_page=10&facets%5Bpage%5D%5B%5D=author&facets%5Bpage%5D%5B%5D=category&facets%5Bpage%5D%5B%5D=tag&facets%5Bpage%5D%5B%5D=object_type&filters%5Bpage%5D%5Btimestamp%5D%5Btype%5D=range&spelling=always&_=1492312830898'.format(article_name)
    #         # print('request+++++++++++++++搜索url：' + search_url)
    #         headers = {
    #             'GET': search_url,
    #             'Host': 'api.swiftype.com',
    #             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    #             'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    #             'Accept-Encoding': 'gzip, deflate, br',
    #             'Connection': 'keep-alive',
    #             'Upgrade-Insecure-Requests': '1',
    #             'If-None-Match': 'W/"3599c41915e7d0abde1422b6e68188fd"',
    #             'Cache-Control': 'max-age=0',
    #         }
    #         request = scrapy.Request(search_url, headers=headers, callback=self.parse_search)
    #         request.meta['article_name'] = article_name
    #         return request
    #
    # def parse_search(self, response):
    #     # print('response==============搜索url：' + response.url)
    #     article_name = response.meta['article_name']
    #     reg = re.compile(r'"url":"(https://techcrunch\.com/\d{4}/\d{2}/\d{2}/[-\w]+/)"')
    #     sear = re.search(reg, response.body_as_unicode())
    #     if not sear:
    #         print('%s》》》》申请json无返回值，放弃寻找此对应英文文章' % article_name)
    #         pass
    #     if len(sear.groups()) == 0:
    #         print('%s》》》》无搜索结果，放弃寻找此对应英文文章' % article_name)
    #         pass
    #     print('%s》》》》找到搜索结果并返回，待确认状态码是否正确' % article_name)
    #     article_url = re.search(reg, response.body_as_unicode()).group(1)
    #     # print('搜索出来的文章：' + article_url)
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
    #     request = scrapy.Request(article_url, headers=headers, callback=self.parse_en)
    #     request.meta['article_name'] = article_name
    #     return request





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