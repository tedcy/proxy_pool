# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyScheduler
   Description :   使用原生threading实现定时任务
   Author :        JHao
   date：          2019/8/5
-------------------------------------------------
   Change Activity:
                   2019/08/05: proxyScheduler
                   2021/02/23: runProxyCheck时,剩余代理少于POOL_SIZE_MIN时执行抓取
                   2023/10/07: 去掉APScheduler，使用原生threading实现定时任务
                   2025/06/03: 支持异步Checker
-------------------------------------------------
"""
__author__ = 'JHao'

import threading
import time
import asyncio
import queue
from helper.fetch import Fetcher
from helper.check import Checker
from helper.memory import MemoryChecker
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler


FETCH_INTERVAL = 4 * 60  # 4分钟
CHECK_INTERVAL = 2 * 60  # 2分钟

fetch_lock = threading.Lock()
check_lock = threading.Lock()


async def __runProxyFetch():
    with fetch_lock:
        proxy_queue = queue.Queue()
        proxy_fetcher = Fetcher()

        for proxy in proxy_fetcher.run():
            proxy_queue.put(proxy)

        await Checker("raw", proxy_queue)


async def __runProxyCheck():
    with check_lock:
        proxy_handler = ProxyHandler()
        proxy_queue = queue.Queue()
        
        for proxy in proxy_handler.getAll():
            proxy_queue.put(proxy)
        
        await Checker("use", proxy_queue)


def fetch_worker():
    log = LogHandler("scheduler")
    while True:
        log.info("启动proxy采集任务")
        try:
            # 创建一个新的事件循环来运行异步函数
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(__runProxyFetch())
            loop.close()
        except Exception as e:
            log.error(f"proxy采集任务异常: {e}")
        time.sleep(FETCH_INTERVAL)


def check_worker():
    log = LogHandler("scheduler")
    while True:
        log.info("启动proxy检查任务")
        try:
            # 创建一个新的事件循环来运行异步函数
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(__runProxyCheck())
            loop.close()
        except Exception as e:
            log.error(f"proxy检查任务异常: {e}")
        time.sleep(CHECK_INTERVAL)


def runScheduler():
    # 启动内存监控
    memory_checker = MemoryChecker()
    memory_checker.start()

    # 启动定时任务线程
    threading.Thread(target=fetch_worker, daemon=True).start()
    threading.Thread(target=check_worker, daemon=True).start()

    # 主线程保持运行
    while True:
        time.sleep(60)


if __name__ == '__main__':
    runScheduler()