# 链家爬虫（成都）
## 环境
* ubuntu 16.04.2 LTS
* python 3.5.2
* pip 8.1.1

## 如何使用
1. pip install -r requirements.txt
2. python main.py

## 原理
测试使用了scrapy内置的Spider, 核心代码位于lianjia.py.
* scrapy启始根据start_urls发送请求， 得到的结果在parse函数中解析，得到不同区域的url;
* 然后使用不同区域的url再次发送请求，得到的结果位于detail_url中解析， 然后针对分页发送批量的请求；
* 解析数据， 最后通过yield item返回

## 注意
导出json格式文件的时候出现对了/000xx之类的乱码；
目前采用csv格式导出，测试通过