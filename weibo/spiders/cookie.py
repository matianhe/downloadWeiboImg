#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import binascii
import base64
import requests
import urllib
import re
import rsa


# com网站的cookie
class Launcher(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.login_url = r'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'  #noqa
        self.prelogin_url = r'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.15)'  #noqa
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'  #noqa
        }

    def get_cookies(self):
        pubkey, servertime, nonce, rsakv = Prelogin(self.prelogin_url)
        post_data = PostData(self.username, self.password, pubkey, servertime,
                             nonce, rsakv)
        session = requests.Session()
        response = session.post(self.login_url, params=post_data,
                                headers=self.headers)
        text = response.content.decode('gbk')
        pa = re.compile(r'location\.replace\(\'(.*?)\'\)')
        redirect_url = pa.search(text).group(1)
        response = session.get(redirect_url, headers=self.headers)
        cookie = requests.utils.dict_from_cookiejar(session.cookies)
        return cookie


def Prelogin(prelogin_url):
    data = requests.get(prelogin_url).content.decode('utf-8')
    p = re.compile('\((.*)\)')
    data_str = p.search(data).group(1)
    server_data_dict = eval(data_str)
    pubkey = server_data_dict['pubkey']
    servertime = server_data_dict['servertime']
    nonce = server_data_dict['nonce']
    rsakv = server_data_dict['rsakv']
    return pubkey, servertime, nonce, rsakv


def PostData(username, password, pubkey, servertime, nonce, rsakv):
    su, sp = RSAEncoder(username, password, pubkey, servertime, nonce)
    post_data = {
        'encoding': 'UTF-8',
        'entry': 'weibo',
        'from': '',
        'gateway': '1',
        'nonce': nonce,
        'pagerefer': '',
        'prelt': '645',
        'pwencode': 'rsa2',
        'returntype': 'META',
        'rsakv': rsakv,
        'savestate': '7',
        'servertime': str(servertime),
        'service': 'miniblog',
        'sp': sp,
        'sr': '1920*1080',
        'su': su,
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack', #noqa
        'useticket': '1',
        'vsnf': '1',
    }
    return post_data


def RSAEncoder(username, password, pubkey, servertime, nonce):
    su_url = urllib.parse.quote_plus(username)
    su_encoded = su_url.encode('utf-8')
    su = base64.b64encode(su_encoded)
    su = su.decode('utf-8')
    rsaPublickey = int(pubkey, 16)
    e = int('10001', 16)
    key = rsa.PublicKey(rsaPublickey, e)
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)
    password = rsa.encrypt(message.encode('utf-8'), key)
    sp = binascii.b2a_hex(password)
    return su, sp




if __name__ == "__main__":
    la = Launcher('account', 'pass')
    cookies = la.get_cookies()
    res = requests.get('https://weibo.com/p/目标微博uid/photos?from=page_100505', 
                headers=la.headers, cookies=cookies)
