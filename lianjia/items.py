# -*- coding: utf-8 -*-
import scrapy


class LianjiaItem(scrapy.Item):
    # 标签 小区 户型 面积 关注人数 观看人数 发布时间 上次交易时间 价格 均价 详情链接 经纬度 城区 id
    title = scrapy.Field()
    community = scrapy.Field()
    model = scrapy.Field()
    area = scrapy.Field()
    focus_num = scrapy.Field()
    watch_num = scrapy.Field()
    publish_time = scrapy.Field()
    last_buy_time = scrapy.Field()
    price = scrapy.Field()
    average_price = scrapy.Field()
    link = scrapy.Field()
    location = scrapy.Field()
    city = scrapy.Field()
    house_id = scrapy.Field()