# -*- coding: utf-8 -*-

import re
import time

import requests
import scrapy
from bs4 import BeautifulSoup

from lianjia.items import LianjiaItem


class LianjiaSpider(scrapy.Spider):
    name = 'lianjiaspider'
    redis_key = 'lianjiaspider:urls'
    start_urls = 'http://cd.lianjia.com/ershoufang/'

    def start_requests(self):
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 \
                         Safari/537.36 SE 2.X MetaSr 1.0'
        headers = {'User-Agent': user_agent}
        yield scrapy.Request(url=self.start_urls, headers=headers, method='GET', callback=self.parse)

    def parse(self, response):
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 \
                                 Safari/537.36 SE 2.X MetaSr 1.0'
        headers = {'User-Agent': user_agent}
        body = response.body.decode('utf-8')
        soup = BeautifulSoup(body)
        area_div = soup.select('div[data-role="ershoufang"]')
        area_list = area_div[0].find_all('a')
        for area in area_list:
            try:
                area_han = area.string    # 地点
                area_pin = area['href'].split('/')[2]   # 拼音
                area_url = 'http://cd.lianjia.com/ershoufang/{}/'.format(area_pin)
                print(area_url)
                yield scrapy.Request(url=area_url, headers=headers, callback=self.detail_url, meta={"id1":area_han,"id2":area_pin} )
            except Exception:
                pass

    # def get_latitude(self,url):  # 进入每个房源链接抓经纬度
    #     p = requests.get(url)
    #     etree = ElementTree()
    #     contents = etree.parse(p.content.decode('utf-8'))
    #     latitude = contents.xpath('/ html / body / script[19]/text()').pop()
    #     time.sleep(3)
    #     regex = '''resblockPosition(.+)'''
    #     items = re.search(regex, latitude)
    #     content = items.group()[:-1]  # 经纬度
    #     longitude_latitude = content.split(':')[1]
    #     return longitude_latitude[1:-1]

    def detail_url(self, response):
        for i in range(1, 101):
            url = 'http://cd.lianjia.com/ershoufang/{}/pg{}/'.format(response.meta["id2"], str(1))
            time.sleep(2)
            try:
                contents = requests.get(url)
                body = contents.content.decode('utf-8')
                soup = BeautifulSoup(body)
                house_ul = soup.find('ul', 'sellListContent')
                houselist = house_ul.find_all('li')
                for house in houselist:
                    try:
                        item = LianjiaItem()
                        item['title'] = house.find('div', 'title').a.string
                        # item['community'] = house.xpath('div[1]/div[2]/div/a/text()').pop()
                        item['model'] = house.find('div', 'houseInfo').text.split('|')[1]

                        area_str = house.find('div', 'houseInfo').text.split('|')[2]
                        area_match = re.findall(r'\d+', area_str)
                        if len(area_match) == 2:
                            item['area'] = float(area_match[0] + '.' + area_match[1])
                        else:
                            item['area'] = float(area_match[0])

                        focus_num_str = house.find('div', 'followInfo').text.split('/')[0]
                        focus_num_match = re.findall(r'\d+', focus_num_str)
                        item['focus_num'] = focus_num_match[0]

                        watch_num_str = house.find('div', 'followInfo').text.split('/')[1]
                        watch_num_match = re.findall(r'\d+', watch_num_str)
                        item['watch_num'] = watch_num_match[0]

                        item['time'] = house.find('div', 'followInfo').text.split('/')[2]
                        item['price'] = float(house.find('div', 'totalPrice').span.string) * 10000

                        average_price_str = house.find('div', 'unitPrice').span.string
                        average_price_match = re.findall(r'\d+', average_price_str)
                        item['average_price'] = average_price_match[0]

                        item['link'] = house.find('div', 'title').a['href']
                        item['city'] = response.meta["id1"]
                        # self.url_detail = house.xpath('div[1]/div[1]/a/@href').pop()
                        # item['Latitude'] = self.get_latitude(self.url_detail)
                    except Exception:
                        pass
                    yield item
            except Exception:
                pass