# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class TedItem(scrapy.Item):
    ranking = scrapy.Field()
    score = scrapy.Field()
    movie_name = scrapy.Field()
    score_num = scrapy.Field()
    # intro = scrapy.Field()


class Ted2Item(scrapy.Item):
    url = scrapy.Field()
    pic_url = scrapy.Field()
    title = scrapy.Field()
    tag = scrapy.Field()
    duration = scrapy.Field()
    source = scrapy.Field()
