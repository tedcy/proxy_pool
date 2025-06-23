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
                   2025/06/03: 转换为基于aiohttp的异步代码
-------------------------------------------------
"""
__author__ = 'JHao'

import asyncio
import aiohttp
from datetime import datetime
import queue
from handler.logHandler import LogHandler
from helper.validator import ProxyValidator
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler


class DoValidator(object):
    """ 执行校验 """

    conf = ConfigHandler()
    log = LogHandler("anonymous")

    @classmethod
    async def anonymousValidator(cls, proxy):
        # 检测代理匿名级别
        anonymous_level = await cls.anonymous(proxy.proxy)
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
    async def validator(cls, proxy, work_type):
        """
        校验入口
        Args:
            proxy: Proxy Object
            work_type: raw/use
        Returns:
            Proxy Object
        """
        http_r = await cls.httpValidator(proxy)
        anonymous_r = False
        if http_r:
            # 别检测https了，用不上，浪费时间
            # proxy.https = await cls.httpsValidator(proxy)
            proxy.https = False
            if proxy.anonymous == '非HTTP代理' or proxy.anonymous == "未知":
                anonymous_r = await cls.anonymousValidator(proxy)
            else :
                # 只可能是透明，匿名，高匿
                if proxy.anonymous in ["匿名代理", "高匿代理"]:
                    anonymous_r = True

        cls.log.info("{}: {} - {} - {}".format(
            proxy.proxy.ljust(23),
            proxy.anonymous,
            http_r, anonymous_r
        ))
        
        proxy.check_count += 1
        proxy.last_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 成功一次就重置失败计数
        if anonymous_r:
            if proxy.fail_count > 0:
                proxy.fail_count = 0
            proxy.last_status = True
        else:
            proxy.fail_count += 1
            proxy.last_status = False
        return proxy

    @classmethod
    async def httpValidator(cls, proxy):
        for func in ProxyValidator.http_validator:
            if not await func(proxy.proxy):
                return False
        return True

    @classmethod
    async def httpsValidator(cls, proxy):
        for func in ProxyValidator.https_validator:
            if not await func(proxy.proxy):
                return False
        return True

    @classmethod
    def preValidator(cls, proxy):
        for func in ProxyValidator.pre_validator:
            if not func(proxy):
                return False
        return True

    @classmethod
    async def anonymous(cls, proxy_addr):
        """
        判断代理的匿名等级：
        0 = Transparent（透明代理）
        1 = Anonymous（匿名代理）
        2 = Elite（高匿代理）
       -1 = Error（检测失败）
        """
        proxy_url = f"http://{proxy_addr}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://httpbin.org/ip', proxy=proxy_url, timeout=aiohttp.ClientTimeout(total=cls.conf.verifyTimeout())) as response:
                    if response.status != 200:
                        cls.log.error(f"anonymousValidator: Proxy {proxy_addr} returned status {response.status}")
                        return -1
                    
                    data = await response.json()
                    origin = data.get('origin', '')
                    headers = {k.lower(): v for k, v in response.headers.items()}
                    
                    # 判断真实IP是否泄露
                    if ',' in origin:
                        return 0  # 透明代理
                    
                    # 判断是否存在代理标识头
                    proxy_headers = ['via', 'proxy-connection', 'x-forwarded-for', 'forwarded']
                    if any(h in headers for h in proxy_headers):
                        return 1  # 匿名代理
                    
                    return 2  # 高匿代理
        except Exception as e:
            cls.log.error(f"anonymousValidator Error occurred while validating proxy {proxy_addr}: {type(e).__name__}: {str(e)}")
            return -1


class _AsyncChecker:
    """ 异步检测 """

    def __init__(self, work_type, target_queue):
        self.work_type = work_type
        # 根据work_type使用不同的日志处理器，将raw checker和use checker的日志划分到不同的文件
        if work_type == "raw":
            self.log = LogHandler("raw_checker")
        else:
            self.log = LogHandler("use_checker")
        self.proxy_handler = ProxyHandler()
        self.target_queue = target_queue
        self.conf = ConfigHandler()
        # 用于统计每个来源的代理数量
        self.total_count_by_source = {}
        # 用于统计每个来源成功的代理数量
        self.success_count_by_source = {}

    async def check_proxy(self, proxy):
        # 更新每个来源的总计数
        for source in proxy._source:
            if source in self.total_count_by_source:
                self.total_count_by_source[source] += 1
            else:
                self.total_count_by_source[source] = 1
                
        proxy = await DoValidator.validator(proxy, self.work_type)
        if self.work_type == "raw":
            await self.__ifRaw(proxy)
        else:
            await self.__ifUse(proxy)

    async def __ifRaw(self, proxy):
        if proxy.last_status:
            if self.proxy_handler.exists(proxy):
                self.log.info('RawProxyCheck: {} exist'.format(proxy.proxy.ljust(23)))
            else:
                self.log.info('RawProxyCheck: {} pass'.format(proxy.proxy.ljust(23)))
                self.proxy_handler.put(proxy)
                # 更新每个来源的成功计数
                for source in proxy._source:
                    if source in self.success_count_by_source:
                        self.success_count_by_source[source] += 1
                    else:
                        self.success_count_by_source[source] = 1
        else:
            self.log.info('RawProxyCheck: {} fail'.format(proxy.proxy.ljust(23)))

    async def __ifUse(self, proxy):
        if proxy.last_status:
            self.log.info('UseProxyCheck: {} pass'.format(proxy.proxy.ljust(23)))
            self.proxy_handler.put(proxy)
            # 更新每个来源的成功计数
            for source in proxy._source:
                if source in self.success_count_by_source:
                    self.success_count_by_source[source] += 1
                else:
                    self.success_count_by_source[source] = 1
        else:
            if proxy.fail_count > self.conf.maxFailCount():
                self.log.info('UseProxyCheck: {} fail, count {} delete'.format(
                    proxy.proxy.ljust(23), proxy.fail_count))
                self.proxy_handler.delete(proxy)
            else:
                self.log.info('UseProxyCheck: {} fail, count {} keep'.format(
                    proxy.proxy.ljust(23), proxy.fail_count))
                self.proxy_handler.put(proxy)

async def safe_check_proxy(proxy, checker, timeout):
    log = LogHandler("safe_checker")
    try:
        await asyncio.wait_for(checker.check_proxy(proxy), timeout=timeout)
    except asyncio.TimeoutError:
        log.error(f"Proxy {proxy.proxy} timed out after {timeout} seconds")
    except Exception as e:
        log.error(f"Proxy {proxy.proxy} raised exception: {repr(e)}")

async def Checker(tp, proxy_queue):
    checker = _AsyncChecker(tp, proxy_queue)
    concurrency = 1000 if tp == "raw" else 20

    while True:
        batch = []
        try:
            # 每次最多取出 concurrency 个元素
            for _ in range(concurrency):
                proxy = proxy_queue.get(block=False)
                batch.append(proxy)
                proxy_queue.task_done()
        except queue.Empty:
            pass

        if not batch:
            # 队列为空，退出循环
            break

        tasks = [safe_check_proxy(proxy, checker, 15) for proxy in batch]
        await asyncio.gather(*tasks)
    
    # 打印每个来源的代理数量统计
    if checker.total_count_by_source:
        checker.log.info("=" * 50)
        checker.log.info("代理统计 (按来源):")
        for source in sorted(checker.total_count_by_source.keys()):
            total = checker.total_count_by_source.get(source, 0)
            success = checker.success_count_by_source.get(source, 0)
            success_rate = (success / total * 100) if total > 0 else 0
            checker.log.info(f"来源: {source} - 总数: {total}, 成功: {success}, 成功率: {success_rate:.2f}%")
        checker.log.info("=" * 50)
        total_all = sum(checker.total_count_by_source.values())
        success_all = sum(checker.success_count_by_source.values())
        success_rate_all = (success_all / total_all * 100) if total_all > 0 else 0
        checker.log.info(f"总计: 总数: {total_all}, 成功: {success_all}, 成功率: {success_rate_all:.2f}%")
