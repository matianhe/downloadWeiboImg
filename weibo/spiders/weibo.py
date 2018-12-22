# !/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import time
import re
from .cookie import Launcher
from weibo.items import WeiboItem
from urllib.parse import urlencode


class Weibo(scrapy.Spider):
    name = 'weibo'
    page_id = 1005053955425715
    la = Launcher('account', 'pass')
    cookies = la.get_cookies()
    headers = la.headers

    def start_requests(self):
        base_url = 'https://weibo.com/p/目标微博uid/photos?from=page_100505'
        yield scrapy.Request(url=base_url, callback=self.parse,
                             cookies=self.cookies, headers=self.headers)

    def parse(self, response):
        ids = re.findall(r'mid=(.+?)&pid=(.+?)&', response.text)
        ids = list(set(ids))
        for item in ids:
            url = ('http://photo.weibo.com/目标微博uid/wbphotos/'
                   'large/mid/{}/pid/{}'.format(item[0], item[1]))
            yield scrapy.Request(url=url, cookies=self.cookies,
                                  callback=self.download, headers=self.headers)


        # 获取ajax参数信息
        match = re.findall(r'owner_uid=(.+)&viewer_uid=(.*)&since_id=(.+?)\\',
                           response.text)
        if match:
            # 拼接next_url
            ajax_url = 'https://weibo.com/p/aj/album/loading?'
            postData = {
                'ajwvr': 6,
                'type': 'photo',
                'owner_uid': match[0][0],
                'viewer_uid': match[0][1],
                'since_id': match[0][2],
                'page_id': self.page_id,
                'ajax_call': 1,
                '_rnd': int(round(time.time()*1000))
            }
            next_url = ajax_url + urlencode(postData)
            yield scrapy.Request(url=next_url, callback=self.parse,
                                 headers=self.cookies, cookies=self.cookies)
        else:
            print('over-------')
            return

    def download(self, response):
        match = re.search(r'id="pic" src="(.+?)"', response.text).group(1)
        item = WeiboItem()
        item['name'] = str(round(time.time()*1000))
        item['url'] = match
        yield item
