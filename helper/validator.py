# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     _validators
   Description :   定义proxy验证方法
   Author :        JHao
   date：          2021/5/25
-------------------------------------------------
   Change Activity:
                   2023/03/10: 支持带用户认证的代理格式 username:password@ip:port
                   2025/06/03: 转换为基于aiohttp的异步代码
-------------------------------------------------
"""
__author__ = 'JHao'

import re
import aiohttp
from util.six import withMetaclass
from util.singleton import Singleton
from util.webRequest import WebRequest
from handler.configHandler import ConfigHandler

from handler.logHandler import LogHandler

log = LogHandler('validator')

conf = ConfigHandler()

HEADER = {'User-Agent': 'curl/7.61.1',
          'Accept': '*/*',
          'Connection': 'keep-alive'}

IP_REGEX = re.compile(r"(.*:.*@)?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}")


class ProxyValidator(withMetaclass(Singleton)):
    pre_validator = []
    http_validator = []
    https_validator = []

    @classmethod
    def addPreValidator(cls, func):
        cls.pre_validator.append(func)
        return func

    @classmethod
    def addHttpValidator(cls, func):
        cls.http_validator.append(func)
        return func

    @classmethod
    def addHttpsValidator(cls, func):
        cls.https_validator.append(func)
        return func


@ProxyValidator.addPreValidator
def formatValidator(proxy):
    """检查代理格式"""
    return True if IP_REGEX.fullmatch(proxy) else False


async def validateProxy(proxy, url, proxy_type='http', ssl=False):
    """通用代理验证函数"""
    proxy_url = f"{proxy_type}://{proxy}"
    timeout = conf.verifyTimeout()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADER, proxy=proxy_url,
                                   timeout=aiohttp.ClientTimeout(total=timeout), ssl=ssl) as response:
                if response.status != 200:
                    log.debug(f"Proxy {proxy} response status: {response.status}")
                    return False

                content_bytes = await response.content.read(3000)
                content = content_bytes.decode('utf-8', errors='ignore')

                ok = '百度一下' in content and '登录' in content
                if ok:
                    log.debug(f"Response True content for {proxy}: {len(content_bytes)} bytes, {content[:320]}...")
                    return True

                log.debug(f"Response False content for {proxy}: {len(content_bytes)} bytes, {content[:320]}...")
                return False
    except Exception as e:
        log.error(f"Error occurred while validating proxy {proxy}: {type(e).__name__}: {str(e)}")
        return False


@ProxyValidator.addHttpValidator
async def httpTimeOutValidator(proxy):
    """http检测超时"""
    return await validateProxy(proxy, conf.httpUrl(), proxy_type='http', ssl=False)


@ProxyValidator.addHttpsValidator
async def httpsTimeOutValidator(proxy):
    """https检测超时"""
    return await validateProxy(proxy, conf.httpsUrl(), proxy_type='https', ssl=False)