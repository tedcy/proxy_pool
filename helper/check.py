# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     check
   Description :   执行代理校验
   Author :        JHao
   date：          2019/8/6
-------------------------------------------------
   Change Activity:
                   2019/08/06: 执行代理校验
                   2021/05/25: 分别校验http和https
                   2022/08/16: 获取代理Region信息
-------------------------------------------------
"""
__author__ = 'JHao'

from util.six import Empty
from threading import Thread
from datetime import datetime
from requests import get
from util.webRequest import WebRequest
from handler.logHandler import LogHandler
from helper.validator import ProxyValidator
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler


class DoValidator(object):
    """ 执行校验 """

    conf = ConfigHandler()
    log = LogHandler("anonymous")

    @classmethod
    def anonymousValidator(cls, proxy):
        # 检测代理匿名级别
        anonymous_level = cls.anonymous(proxy.proxy, proxy.https)
        # 只保留匿名代理和高匿代理，过滤掉透明代理
        if anonymous_level == 0:
            proxy.anonymous = "透明代理"
            return False
        if anonymous_level == 1:
            proxy.anonymous = "匿名代理"
            return True
        if anonymous_level == 2:
            proxy.anonymous = "高匿代理"
            return True
        proxy.anonymous = "未知"
        return False

    @classmethod
    def validator(cls, proxy, work_type):
        """
        校验入口
        Args:
            proxy: Proxy Object
            work_type: raw/use
        Returns:
            Proxy Object
        """
        http_r = cls.httpValidator(proxy)
        anonymous_r = False
        if http_r:
            proxy.https = cls.httpsValidator(proxy)
            anonymous_r = cls.anonymousValidator(proxy)

        cls.log.info("{}: {} - {} - {}".format(
            proxy.proxy.ljust(23),
            proxy.anonymous,
            http_r, anonymous_r
        ))
        
        proxy.check_count += 1
        proxy.last_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if anonymous_r:
            if proxy.fail_count > 0:
                proxy.fail_count -= 1
            proxy.last_status = True
        else:
            proxy.fail_count += 1
            proxy.last_status = False
        return proxy

    @classmethod
    def httpValidator(cls, proxy):
        for func in ProxyValidator.http_validator:
            if not func(proxy.proxy):
                return False
        return True

    @classmethod
    def httpsValidator(cls, proxy):
        for func in ProxyValidator.https_validator:
            if not func(proxy.proxy):
                return False
        return True

    @classmethod
    def preValidator(cls, proxy):
        for func in ProxyValidator.pre_validator:
            if not func(proxy):
                return False
        return True

    @classmethod
    def anonymous(cls, proxy_addr, https=False, timeout=5.0):
        """
        判断代理的匿名等级：
        0 = Transparent（透明代理）
        1 = Anonymous（匿名代理）
        2 = Elite（高匿代理）
       -1 = Error（检测失败）
        """
        scheme = 'https' if https else 'http'
        url = f'{scheme}://httpbin.org/ip'
        proxies = {scheme: f"{scheme}://{proxy_addr}"}
        try:
            r = get(url, proxies=proxies, timeout=timeout)
            if r.status_code != 200:
                return -1
            origin = r.json().get('origin', '')
            headers = dict((k.lower(), v) for k, v in r.headers.items())
            # 判断真实IP是否泄露
            if ',' in origin:
                return 0  # 透明代理
            # 判断是否存在代理标识头
            proxy_headers = ['via', 'proxy-connection', 'x-forwarded-for', 'forwarded']
            if any(h in headers for h in proxy_headers):
                return 1  # 匿名代理
            return 2  # 高匿代理
        except Exception as e:
            print(f"anonymousValidator Error: {str(e)}")
            return -1


class _ThreadChecker(Thread):
    """ 多线程检测 """

    def __init__(self, work_type, target_queue, thread_name):
        Thread.__init__(self, name=thread_name)
        self.work_type = work_type
        # 根据work_type使用不同的日志处理器，将raw checker和use checker的日志划分到不同的文件
        if work_type == "raw":
            self.log = LogHandler("raw_checker")
        else:
            self.log = LogHandler("use_checker")
        self.proxy_handler = ProxyHandler()
        self.target_queue = target_queue
        self.conf = ConfigHandler()

    def run(self):
        self.log.info("{}ProxyCheck - {}: start".format(self.work_type.title(), self.name))
        while True:
            try:
                proxy = self.target_queue.get(block=False)
            except Empty:
                self.log.info("{}ProxyCheck - {}: complete".format(self.work_type.title(), self.name))
                break
            proxy = DoValidator.validator(proxy, self.work_type)
            if self.work_type == "raw":
                self.__ifRaw(proxy)
            else:
                self.__ifUse(proxy)
            self.target_queue.task_done()

    def __ifRaw(self, proxy):
        if proxy.last_status:
            if self.proxy_handler.exists(proxy):
                self.log.info('RawProxyCheck - {}: {} exist'.format(self.name, proxy.proxy.ljust(23)))
            else:
                self.log.info('RawProxyCheck - {}: {} pass'.format(self.name, proxy.proxy.ljust(23)))
                self.proxy_handler.put(proxy)
        else:
            self.log.info('RawProxyCheck - {}: {} fail'.format(self.name, proxy.proxy.ljust(23)))

    def __ifUse(self, proxy):
        if proxy.last_status:
            self.log.info('UseProxyCheck - {}: {} pass'.format(self.name, proxy.proxy.ljust(23)))
            self.proxy_handler.put(proxy)
        else:
            if proxy.fail_count > self.conf.maxFailCount():
                self.log.info('UseProxyCheck - {}: {} fail, count {} delete'.format(self.name,
                                                                                    proxy.proxy.ljust(23),
                                                                                    proxy.fail_count))
                self.proxy_handler.delete(proxy)
            else:
                self.log.info('UseProxyCheck - {}: {} fail, count {} keep'.format(self.name,
                                                                                  proxy.proxy.ljust(23),
                                                                                  proxy.fail_count))
                self.proxy_handler.put(proxy)


def Checker(tp, queue):
    """
    run Proxy ThreadChecker
    :param tp: raw/use
    :param queue: Proxy Queue
    :return:
    """
    thread_list = list()
    count = 20
    if tp == "raw":
        count = 200
    for index in range(count):
        thread_list.append(_ThreadChecker(tp, queue, "thread_%s" % str(index).zfill(2)))

    for thread in thread_list:
        thread.setDaemon(True)
        thread.start()
    
    for thread in thread_list:
        thread.join()
