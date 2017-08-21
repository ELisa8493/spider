# -*- coding: utf-8 -*-

import re
import time

import requests
import scrapy
from bs4 import BeautifulSoup

from items import LianjiaItem
from helper.transCookie import transCookie

cookie_str = 'lianjia_uuid=f56fda39-e0f9-4bf4-aceb-aeb8bb6ff179; gr_user_id=49a62d12-07a6-4590-9610-8ab94cca89e8; UM_distinctid=15da14b2d8379c-0cacf1d2dd387d-38750f56-1fa400-15da14b2d84727; _jzqy=1.1501649645.1501722580.1.jzqsr=baidu|jzqct=%E9%93%BE%E5%AE%B6.-; select_city=510100; _jzqckmp=1; _jzqx=1.1502934514.1502934514.1.jzqsr=captcha%2Elianjia%2Ecom|jzqct=/.-; all-lj=6341ae6e32895385b04aae0cf3d794b0; gr_session_id_a1a50f141657a94e=bb4983a3-a7c4-40c0-b988-b420fbcb0c7c; Hm_lvt_9152f8221cb6243a53c83b956842be8a=1501722579,1502871254,1502934514,1502952920; Hm_lpvt_9152f8221cb6243a53c83b956842be8a=1502952931; CNZZDATA1253492306=2124281406-1501648005-null%7C1502950619; _smt_uid=59815aec.46e66fb1; CNZZDATA1254525948=1858624088-1501647278-null%7C1502952507; CNZZDATA1255633284=298962160-1501646323-null%7C1502951659; CNZZDATA1255604082=498907718-1501645227-null%7C1502949428; _qzja=1.196317582.1501649645070.1502934513969.1502952919902.1502952919902.1502952932268.0.0.0.31.5; _qzjb=1.1502952919901.2.0.0.0; _qzjc=1; _qzjto=17.2.0; _jzqa=1.3601391487608853500.1501649645.1502934514.1502952920.5; _jzqc=1; _jzqb=1.2.10.1502952920.1; _ga=GA1.2.401334872.1501649648; _gid=GA1.2.141856389.1502871258; lianjia_ssid=c09446af-f271-474e-9157-1db1737f7d19'
trans = transCookie(cookie_str)

class LianjiaSpider(scrapy.Spider):
    name = 'lianjiaspider'
    start_urls = 'http://cd.lianjia.com/ershoufang/'
    cookie = trans.stringToDict()
    headers = {
        'Host': "cd.lianjia.com",
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'DNT': '1',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'en-US,en;q=0.8,zh;q=0.6',
    }

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls, headers=self.headers, method='GET', cookies=self.cookie, callback=self.parse)

    def parse(self, response):
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
                time.sleep(5)
                yield scrapy.Request(url=area_url, headers=self.headers, cookies=self.cookie, callback=self.detail_url, meta={"id1": area_han, "id2": area_pin} )
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
            time.sleep(5)
            try:
                contents = requests.get(url, headers=self.headers, cookies=self.cookie)
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