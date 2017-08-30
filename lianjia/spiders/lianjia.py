# -*- coding: utf-8 -*-
import re
import time

import scrapy
from bs4 import BeautifulSoup

from lianjia.items import LianjiaItem
from helper.transCookie import transCookie

cookie_str = 'lianjia_uuid=f56fda39-e0f9-4bf4-aceb-aeb8bb6ff179; gr_user_id=49a62d12-07a6-4590-9610-8ab94cca89e8; UM_distinctid=15da14b2d8379c-0cacf1d2dd387d-38750f56-1fa400-15da14b2d84727; _jzqy=1.1501649645.1501722580.1.jzqsr=baidu|jzqct=%E9%93%BE%E5%AE%B6.-; _jzqx=1.1502934514.1502934514.1.jzqsr=captcha%2Elianjia%2Ecom|jzqct=/.-; select_city=510100; all-lj=0f6b18681ea67d53fa44b1df18064287; _jzqckmp=1; _smt_uid=59815aec.46e66fb1; gr_session_id_a1a50f141657a94e=e66b3bfb-5b3c-4106-a393-f8dbc1b0ca11; CNZZDATA1253492306=2124281406-1501648005-null%7C1503558640; Hm_lvt_9152f8221cb6243a53c83b956842be8a=1502871254,1502934514,1502952920,1503555027; Hm_lpvt_9152f8221cb6243a53c83b956842be8a=1503560620; CNZZDATA1254525948=1858624088-1501647278-null%7C1503557179; CNZZDATA1255633284=298962160-1501646323-null%7C1503557380; CNZZDATA1255604082=498907718-1501645227-null%7C1503555880; _qzja=1.196317582.1501649645070.1503555027518.1503560616864.1503560616864.1503560620186.0.0.0.44.7; _qzjb=1.1503560616864.2.0.0.0; _qzjc=1; _qzjto=8.2.0; _jzqa=1.3601391487608853500.1501649645.1503555027.1503560617.7; _jzqc=1; _jzqb=1.2.10.1503560617.1; _ga=GA1.2.401334872.1501649648; _gid=GA1.2.608001822.1503555030; lianjia_ssid=0b7105ec-a14d-46f9-a7c6-e29fae3f5cd4'
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
                area_page1_url = 'http://cd.lianjia.com/ershoufang/{}/'.format(area_pin)

                # 首页
                yield scrapy.Request(url=area_page1_url, headers=self.headers, cookies=self.cookie, callback=self.get_pg_info, meta={"id1": area_han, "id2": area_pin})

                # 剩下的页面
                for i in range(2, 101):
                    area_pages_url = 'http://cd.lianjia.com/ershoufang/{}/pg{}/'.format(area_pin, str(1))
                    yield scrapy.Request(url=area_pages_url, headers=self.headers, cookies=self.cookie, callback=self.get_pg_info, meta={"id1": area_han, "id2": area_pin})
            except Exception as e:
                print(str(e))
                pass

    def get_pg_info(self, response):
        body = response.body.decode('utf-8')
        soup = BeautifulSoup(body)
        house_ul = soup.find('ul', 'sellListContent')
        house_list = house_ul.find_all('li')
        for house in house_list:
            try:
                item = LianjiaItem()
                item['title'] = house.find('div', 'title').a.string
                item['community'] = house.find('div', 'houseInfo').text.split('|')[0]
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

                item['price'] = float(house.find('div', 'totalPrice').span.string) * 10000

                average_price_str = house.find('div', 'unitPrice').span.string
                average_price_match = re.findall(r'\d+', average_price_str)
                item['average_price'] = average_price_match[0]

                item['link'] = house.find('div', 'title').a['href']
                item['city'] = response.meta["id1"]

                yield scrapy.Request(url=item['link'], headers=self.headers, cookies=self.cookie, callback=self.get_detail_info, meta={"item": item} )
            except Exception as e:
                print(str(e))
                pass

    def get_detail_info(self, response):
        body = response.body.decode('utf-8')
        soup = BeautifulSoup(body)
        transaction_div = soup.find('div', 'transaction')
        transaction_lis = transaction_div.find_all('li')
        item = response.meta["item"]
        item['last_buy_time'] = transaction_lis[2].text[4:]
        item['publish_time'] = transaction_lis[0].text[4:]

        regex = '''resblockPosition(.+)'''
        items = re.search(regex, body)
        content = items.group()[:-1]  # 经纬度
        longitude_latitude = content.split(':')[1]
        item['location'] = longitude_latitude[1:-1]

        id_regex = '''houseId(.+)'''
        ids = re.search(id_regex, body)
        house_id_str = ids.group()[:-1]  # house id
        house_id = house_id_str.split(':')[1]
        item['house_id'] = house_id[1:-1]

        yield item
