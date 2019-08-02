# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DigikalacrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    product_id = scrapy.Field()
    product_title = scrapy.Field()
    brand = scrapy.Field()
    cat = scrapy.Field()
    price = scrapy.Field()
    star_rating = scrapy.Field()
    n_peaple_voted = scrapy.Field()
    overview = scrapy.Field()
    n_peaple_Recommended = scrapy.Field()
    linkto = scrapy.Field()
    # comments is a list of json objects to store comments for each product
    comments = scrapy.Field()
