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
-------------------------------------------------
"""
__author__ = 'JHao'

import re
from requests import get
from util.six import withMetaclass
from util.singleton import Singleton
from util.webRequest import WebRequest
from handler.configHandler import ConfigHandler

from handler.logHandler import LogHandler

log = LogHandler('validator')

conf = ConfigHandler()

HEADER = {'User-Agent': WebRequest().user_agent,
          'Accept': '*/*',
          'Connection': 'keep-alive',
          'Accept-Language': 'zh-CN,zh;q=0.8'}
#加上user_agent会变成桌面端响应
HEADER = {}

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


@ProxyValidator.addHttpValidator
def httpTimeOutValidator(proxy):
    """ http检测超时 """

    proxies = {"http": "http://{proxy}".format(proxy=proxy)}

    try:
        r = get(conf.httpUrl(), headers=HEADER, proxies=proxies, timeout=conf.verifyTimeout())
        content = r.content.decode('utf-8', errors='ignore')
        ok = '百度一下' in content and '登录' in content
        if ok:
            return True
        log.debug(f"Response False content for {proxy}: {r.text[0: 100]}...")
        return False
    except Exception as e:
        log.error(f"Error occurred while validating proxy {proxy}: {str(e)}")
        return False


@ProxyValidator.addHttpsValidator
def httpsTimeOutValidator(proxy):
    """https检测超时"""

    proxies = {"https": "https://{proxy}".format(proxy=proxy)}
    try:
        r = get(conf.httpsUrl(), headers=HEADER, proxies=proxies, timeout=conf.verifyTimeout(), verify=False)
        content = r.content.decode('utf-8', errors='ignore')
        ok = '百度一下' in content and '登录' in content
        if ok:
            return True
        log.debug(f"Response False content for {proxy}: {r.text[0: 100]}...")
        return False
    except Exception as e:
        log.error(f"Error occurred while validating proxy {proxy}: {str(e)}")
        return False


@ProxyValidator.addHttpValidator
def customValidatorExample(proxy):
    """自定义validator函数，校验代理是否可用, 返回True/False"""
    return True
