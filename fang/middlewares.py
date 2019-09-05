# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random
import requests


class UserAgent(object):
    def process_request(self, request, spider):
        # 在百度里搜索user_agent_list粘进来
        user_agent_list = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        ]
        agent = random.choice(user_agent_list)
        # 同样在setting里开启
        request.headers['user-agent'] = agent


class ProxyMiddleware(object):
    def __init__(self, proxy_url):
        self.proxy_url = proxy_url

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            proxy_url=crawler.settings.get('PROXY_URL')
        )

    def get_random_proxy(self):
        # 请求目标url获取随机ip
        try:
            response = requests.get(self.proxy_url)
            response.raise_for_status()
            proxy = response.text
            return proxy
        except:
            print('ip请求失败')

    def process_request(self, request, spider):
        # 使用代理池中的ip发起请求
        # retry_times，当第一次请求失败时再启动代理ip。因为本机ip更稳定
        if request.meta.get('retry_times'):
            proxy = self.get_random_proxy()  # 180.104.2.55:8888
            if proxy:
                apply = str(request).split(':')[0]  # <GET https、<GET http
                if apply == '<GET https':
                    uri = 'https://{proxy}'.format(proxy=proxy)
                else:
                    uri = 'http://{proxy}'.format(proxy=proxy)
                print('正在使用代理', uri, '      爬取：', request)
                request.meta['proxy'] = uri
                uri = 'https://{proxy}'.format(proxy=proxy)
                print('正在使用代理', uri, '   处理：', request)
                request.meta['proxy'] = uri


class CaptchaMiddleware(object):

    def process_response(self, request, response, spider):
        # 验证码格式   'http://search.fang.com/captcha-verify/redirect?h=https://esf.fang.com/house/h316-i31/'
        # 如果出现验证码,处理url，重新放入调度队列
        if 'captcha-verify' in response.url:
            print('出现验证码，重新放入调度队列')
            # http://search.fang.com/captcha-verify/redirect?h=https://pinghu.esf.fang.com/house/h316-i35/
            print('出现验证码的url是：', response.url)
            request = str(request).replace('http://search.fang.com/captcha-verify/redirect?h=', '')
            print('放入调度队列的url是：', request)  # <GET https://pinghu.esf.fang.com/house/h316-i35/>
            return request
        elif '跳转...' in response.text:
            return request
        elif response.status == 200:
            return response
