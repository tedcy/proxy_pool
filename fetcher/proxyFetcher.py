# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyFetcher
   Description :
   Author :        JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25: proxyFetcher
-------------------------------------------------
"""
__author__ = 'JHao'

import re
import json
from time import sleep
from bs4 import BeautifulSoup

from util.webRequest import WebRequest


class ProxyFetcher(object):
    """
    proxy getter
    """

    @staticmethod
    def freeProxy01():
        """ 开心代理 """
        target_urls = ["http://www.kxdaili.com/dailiip.html", "http://www.kxdaili.com/dailiip/2/1.html"]
        for url in target_urls:
            tree = WebRequest().get(url).tree
            for tr in tree.xpath("//table[@class='active']//tr")[1:]:
                ip = "".join(tr.xpath('./td[1]/text()')).strip()
                port = "".join(tr.xpath('./td[2]/text()')).strip()
                yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy02():
        """ 稻壳代理 https://www.docip.net/ """
        r = WebRequest().get("https://www.docip.net/data/free.json", timeout=10)
        try:
            for each in r.json['data']:
                yield each['ip']
        except Exception as e:
            print(e)

    @staticmethod
    def freeProxy03():
        urls = [
            'https://openproxylist.xyz/http.txt',
            'http://pubproxy.com/api/proxy?limit=3&format=txt&http=true&type=https',
            'https://www.proxy-list.download/api/v1/get?type=https',
            'https://raw.githubusercontent.com/shiftytr/proxy-list/master/proxy.txt'
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=20)
            for proxy in r.text.split('\n'):
                if proxy:
                    yield proxy

    @staticmethod
    def freeProxy0405(daili_url):
        for i in range(1, 20):
            sleep(1)
            try:
                url = daili_url.format(i)
                r = WebRequest().get(url, timeout=20)

                # 假设网页内容中有一段包含 JSON 格式的 fpsList 数据
                # 使用 BeautifulSoup 解析网页
                soup = BeautifulSoup(r.text, 'html.parser')
                script_tags = soup.find_all('script')

                for script in script_tags:
                    if "const fpsList" in script.text:
                        json_text = re.search(r'const fpsList = (.*?);', script.text, re.DOTALL)
                        if json_text:
                            data = json.loads(json_text.group(1))
                            break

                # 提取 fpsList
                if 'data' in locals():
                    fps_list = data
                    for fps in fps_list:
                        ip = fps.get("ip")
                        port = fps.get("port")
                        yield f"{ip}:{port}"
            except Exception as e:
                print(e)

    @staticmethod
    def freeProxy04():
        #return ProxyFetcher.freeProxy0405('https://www.kuaidaili.com/free/inha/{}/') 
        urls = [
            'https://raw.githubusercontent.com/parserpp/ip_ports/main/proxyinfo.txt'
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=20)
            for proxy in r.text.split('\n'):
                if proxy:
                    yield proxy

    @staticmethod
    def freeProxy05():
        return ProxyFetcher.freeProxy0405('https://www.jiliuip.com/free/{}/')

    @staticmethod
    def customProxy01():
        """
        返回格式为 ip:port，仅获取HTTP和HTTPS代理
        """
        urls = [
            'https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/http.txt',
            'https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/https.txt',
            'https://raw.githubusercontent.com/proxifly/free-proxy-list/refs/heads/main/proxies/protocols/http/data.txt',
            'https://www.proxy-list.download/api/v1/get?type=http',
            'https://api.openproxylist.xyz/http.txt',
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=20)
            for proxy in r.text.split('\n'):
                if proxy:
                    if proxy.startswith("http://"):
                        proxy = proxy[len("http://"):]
                    elif proxy.startswith("https://"):
                        proxy = proxy[len("https://"):]
                    yield proxy


if __name__ == '__main__':
    p = ProxyFetcher()
    for _ in p.freeProxy06():
        print(_)

# http://nntime.com/proxy-list-01.htm
