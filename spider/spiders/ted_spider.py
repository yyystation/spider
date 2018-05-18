# encoding: utf-8
"""
@author: yanyong.yan
@contact: yyyjoyce@hotmail.com
@file: ted_spider.py.py
@time: 2018/5/15 0015 18:32
"""
import datetime
import scrapy
from scrapy import Request
import requests
from spider.items import TedItem, Ted2Item


class TedSpider(scrapy.Spider):
    name = "ted"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
    }

    def start_requests(self):
        url = "https://movie.douban.com/top250"
        yield Request(url, headers=self.headers)

    def parse(self, response):
        item = TedItem()
        movies = response.xpath('//ol[@class="grid_view"]/li')
        for movie in movies:
            item['ranking'] = movie.xpath(
                './/div[@class="pic"]/em/text()').extract()[0]
            item['movie_name'] = movie.xpath(
                './/div[@class="hd"]/a/span[1]/text()').extract()[0]
            item['score'] = movie.xpath(
                './/div[@class="star"]/span[@class="rating_num"]/text()'
            ).extract()[0]
            item['score_num'] = movie.xpath(
                './/div[@class="star"]/span/text()').re(r'(\d+)人评价')[0]
            yield item

        next_url = response.xpath('//span[@class="next"]/a/@href').extract()
        if next_url:
            next_url = 'https://movie.douban.com/top250' + next_url[0]
            yield Request(next_url, headers=self.headers)


class TedSpider2(scrapy.Spider):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        response = requests.get("https://www.ted.com/topics/combo?models=Talks")
        self.tag_lst = response.json()

    name = "ted2"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
    }

    def start_requests(self):
        for tag in self.tag_lst:
            url = "https://www.ted.com/talks?sort=newest&topics%5B%5D={}".format(tag["label"])
            url = url.replace(" ", "+")
            # url = "https://www.ted.com/talks?sort=newest&topics%5B%5D=3d+printing"
            yield Request(url, headers=self.headers)

    def parse(self, response):
        item = Ted2Item()
        item['source'] = response.xpath('.//title/text()').extract()[0]
        item["view_num"] = 0
        item["intro"] = "no intro"
        item['like_num'] = 0
        item['comment_num'] = 0
        item["update_time"] = datetime.datetime.now().__str__()
        item['tag'] = response.xpath(
            './/span[@class="stub__label"]/text()').extract()[0]
        movies = response.xpath('.//div[@class="row row-sm-4up row-lg-6up row-skinny"]/div[@class="col"]')
        for movie in movies:
            item['url'] = "https://www.ted.com" + movie.xpath(
                './/a[@class=" ga-link"]/@href').extract()[0]
            item['pic_url'] = movie.xpath(
                './/img[@class=" thumb__image"]/@src').extract()[0].split("?")[0]
            item['title'] = movie.xpath(
                './/a[@class=" ga-link"]/text()').extract()[2].strip("\n")
            item['duration'] = movie.xpath(
                './/span[@class="thumb__duration"]/text()').extract()[0].strip("\"")
            yield item

        next_url = response.xpath('//a[@class="pagination__next pagination__flipper pagination__link"]/@href').extract()
        if next_url:
            next_url = 'https://www.ted.com' + next_url[0]
            yield Request(next_url, headers=self.headers)
