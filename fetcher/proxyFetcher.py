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

import base64
import re
import json
from time import sleep
from bs4 import BeautifulSoup
import quickjs

from util.webRequest import WebRequest

from handler.configHandler import ConfigHandler
conf = ConfigHandler()
ctx = quickjs.Context()

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
            'http://pubproxy.com/api/proxy?limit=3&format=txt&http=true&type=http',
            'https://www.proxy-list.download/api/v1/get?type=http',
            'https://raw.githubusercontent.com/shiftytr/proxy-list/master/proxy.txt'
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=20)
            for proxy in r.text.split('\n'):
                if proxy:
                    yield proxy

    @staticmethod
    def freeProxy04():
        urls = [
            'https://raw.githubusercontent.com/parserpp/ip_ports/main/proxyinfo.txt'
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=20)
            for proxy in r.text.split('\n'):
                if proxy:
                    yield proxy

    @staticmethod
    def freeProxy05Base(daili_url):
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
    def freeProxy05():
        return ProxyFetcher.freeProxy05Base('https://www.jiliuip.com/free/{}/')

    @staticmethod
    def freeProxy06():
        """
        返回格式为 ip:port，仅获取HTTP和HTTPS代理
        """
        urls = [
            'https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/http.txt',
            'https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/https.txt',
            'https://raw.githubusercontent.com/proxifly/free-proxy-list/refs/heads/main/proxies/protocols/http/data.txt',
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

    @staticmethod
    def freeProxy07():
        """
        站大爷 https://www.zdaye.com/dayProxy.html
        """
        for i in range(1, 5):
            url = 'https://www.zdaye.com/free/{}'.format("" if i == 1 else i)
            html_tree = WebRequest().get(url, verify=False).tree
            for tr in html_tree.xpath("//table//tr"):
                ip = "".join(tr.xpath("./td[1]/text()")).strip()
                port = "".join(tr.xpath("./td[2]/text()")).strip()
                yield "%s:%s" % (ip, port)
            sleep(8)
    
    @staticmethod
    def freeProxy08():
        """ FreeProxyList https://free-proxy-list.net"""
        url = 'https://free-proxy-list.net'
        html_tree = WebRequest().get(url, verify=False).tree
        proxies = html_tree.xpath("//*[@id='raw']/div/div/div[2]/textarea/text()")
        matches = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+', proxies[0])
        for proxy in matches:
            yield proxy

    @staticmethod
    def freeProxy09(page_count=8):
        """ 快代理 https://www.kuaidaili.com """
        url_pattern = [
            'https://www.kuaidaili.com/free/inha/{}/',
            'https://www.kuaidaili.com/free/intr/{}/',
            'https://www.kuaidaili.com/free/fps/{}/'
        ]
        url_list = []
        for page_index in range(1, page_count + 1):
            for pattern in url_pattern:
                url_list.append(pattern.format(page_index))
        for url in url_list:
            text = WebRequest().get(url).text
            pattern = re.compile(r'fpsList\s*=\s*(\[\s*\{.*?\}\s*\])', re.S)
            match = pattern.search(text)
            if not match:
                continue
            json_str = match.group(1)
            data = json.loads(json_str)
            for proxy in data:
                yield "%s:%s" % (proxy['ip'], proxy['port'])
            sleep(5)  # 必须sleep 不然第二条请求不到数据

    @staticmethod
    def freeProxy10():
        """
        https://proxy-list.org/english/index.php
        :return:
        """
        urls = ['https://proxy-list.org/english/index.php?p=%s' % n for n in range(1, 10)]
        request = WebRequest()
        import base64
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r"Proxy\('(.*?)'\)", r.text)
            for proxy in proxies:
                yield base64.b64decode(proxy).decode()
            sleep(2)

    @staticmethod
    def freeProxy11(page_count=3):
        http_pattern = [
            'https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-{}'
        ]
        url_list = []
        for page_index in range(1, page_count + 1):
            for pattern in http_pattern:
                url_list.append(pattern.format(page_index))
        request = WebRequest()
        for url in url_list:
            r = request.get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ':'.join(proxy)
            sleep(2)

    @staticmethod
    def freeProxy12(page_count=3):
        for i in range(1, page_count + 1):
            url = 'https://proxylist.geonode.com/api/proxy-list?limit=100&page={}&sort_by=lastChecked&sort_type=desc'.format(
                i)
            data = WebRequest().get(url, timeout=10).json['data']
            for each in data:
                yield "%s:%s" % (each['ip'], each['port'])
            sleep(5)

    @staticmethod
    def freeProxy13(page_count=5):
        for i in range(1, page_count + 1):
            url = 'https://www.freeproxy.world/?type=&anonymity=&country=&speed=&port=&page={}'.format(i)
            html_tree = WebRequest().get(url, timeout=10).tree
            for tr in html_tree.xpath("//table//tr"):
                ip = "".join(tr.xpath("./td[1]/text()")).strip()
                port = "".join(tr.xpath("./td[2]/a/text()")).strip()
                if ip and port:
                    yield "%s:%s" % (ip, port)
            sleep(2)

    @staticmethod
    def freeProxy14(page_count=3):
        for i in range(1, page_count + 1):
            url = 'https://freeproxylist.cc/servers/{}.html'.format(i)
            text = WebRequest().get(url, timeout=10).text
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', text)
            for proxy in proxies:
                yield ':'.join(proxy)
            sleep(5)

    @staticmethod
    def freeProxy15(page_count=8):
        for i in range(1, page_count + 1):
            url = 'https://cn.proxy-tools.com/proxy{}'.format("/" if i == 1 else ('?page=' + str(i)))
            html_tree = WebRequest().get(url, timeout=10).tree
            for tr in html_tree.xpath("//table//tr"):
                ip = "".join(tr.xpath("./td[1]/text()")).strip()
                port = 80
                if ip and port:
                    yield "%s:%s" % (ip, port)
            sleep(5)

    @staticmethod
    def freeProxy16():
        """ 小幻HTTP代理 """
        url = 'https://ip.ihuan.me/today.html'
        request = WebRequest(url)
        html_tree = request.Session(url, timeout=10).tree
        href = html_tree.xpath("/html/body//div[2]/div/div/div[1]/a/@href")[0]
        sleep(2)
        href_text = request.Session('https://ip.ihuan.me' + href, timeout=10).text
        matches = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+', href_text)
        for proxy in matches:
            yield proxy

    @staticmethod
    def freeProxy17(page_count=5):
        """ 89免费代理 """
        url = 'https://www.89ip.cn/'
        request = WebRequest(url)
        for i in range(1, page_count + 1):
            url = 'https://www.89ip.cn/{}'.format("" if i == 1 else ('index_{}.html'.format(i)))
            html_tree = request.Session(url, timeout=10).tree
            for tr in html_tree.xpath("//table//tr"):
                ip = "".join(tr.xpath("./td[1]/text()")).strip()
                port = "".join(tr.xpath("./td[2]/text()")).strip()
                if ip and port:
                    yield "%s:%s" % (ip, port)
            sleep(3)

    @staticmethod
    def freeProxy18():
        """ 齐云代理 """
        url = 'https://www.qiyunip.com/freeProxy/'
        html_tree = WebRequest().get(url, timeout=10).tree
        for tr in html_tree.xpath("//table//tr"):
            ip = "".join(tr.xpath("./th[1]/text()")).strip()
            port = "".join(tr.xpath("./th[2]/text()")).strip()
            if ip and port:
                yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy19():
        """ proxy5 """
        url = 'https://proxy5.net/cn/free-proxy'
        html_tree = WebRequest().get(url, timeout=10).tree
        for tr in html_tree.xpath("//table//tr"):
            ip = "".join(tr.xpath("./td[1]/strong/text()")).strip()
            port = "".join(tr.xpath("./td[2]/text()")).strip()
            if ip and port:
                yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy20(use_local_data=False):
        """ proxynova """
        def extract_expr(s: str) -> str:
            start = s.find('(') + 1
            end = s.rfind(')')
            if start == 0 or end == -1:
                raise ValueError("无法在字符串中找到匹配的括号")
            return s[start:end]

        def decode_atob_in_js(js_code: str) -> str:
            """
            将 js_code 中所有 atob("…") 调用替换为对应的解码后字符串，
            比如 atob("NDcuMjU0LjM=") -> "47.254.3"
            """
            # 匹配 atob("…") 并捕获内部的 base64 文本
            pattern = re.compile(r'atob\("([^"]+)"\)')

            def _repl(m: re.Match) -> str:
                b64_str = m.group(1)
                try:
                    decoded = base64.b64decode(b64_str).decode('utf-8')
                except Exception:
                    return m.group(0)
                return f'"{decoded}"'

            return pattern.sub(_repl, js_code)

        if use_local_data:
            # 使用本地数据文件
            from lxml import etree
            try:
                with open('freeProxy20.html', 'r', encoding='utf-8') as f:
                    content = f.read()
                html_tree = etree.HTML(content)
            except Exception as e:
                print(f"读取本地数据文件失败: {e}")
                return
        else:
            # 使用网络请求
            url = 'https://www.proxynova.com/proxy-server-list/'
            html_tree = WebRequest().get(url, timeout=10).tree
        for tr in html_tree.xpath("//*[@id='tbl_proxy_list']/tbody/tr"):
            js_tree = tr.xpath("./td[1]//script/text()")
            js_code = extract_expr(js_tree[0])
            if 'atob(' in js_code:
                js_code = decode_atob_in_js(js_code)
            ip = ctx.eval(js_code)
            port = "".join(tr.xpath("./td[2]/text()")).strip()
            if ip and port:
                yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy21(page_count = 2, use_local_data=False):
        """ proxydb """
        for i in range(0, page_count):
            if use_local_data:
                # 使用本地数据文件
                from lxml import etree
                try:
                    with open('freeProxy21.html', 'r', encoding='utf-8') as f:
                        content = f.read()
                    html_tree = etree.HTML(content)
                except Exception as e:
                    print(f"读取本地数据文件失败: {e}")
                    return
            else:
                url = 'https://proxydb.net/'
                params = {
                    'protocol': 'http',
                    'anonlvl': '4',
                    'country': '',
                    'offset': i * 30
                }
                html_tree = WebRequest().get(url, params=params, timeout=10).tree
            
            # 提取表格中的代理信息
            for tr in html_tree.xpath("//table[@class='table table-sm table-hover table-striped']/tbody/tr"):
                # 提取IP地址
                ip_element = tr.xpath("./td[1]/a/text()")
                if not ip_element:
                    continue
                ip = ip_element[0].strip()
                
                # 提取端口
                port_element = tr.xpath("./td[2]/a/text()")
                if not port_element:
                    continue
                port = port_element[0].strip()
                
                # 组合成代理地址
                if ip and port:
                    yield "%s:%s" % (ip, port)