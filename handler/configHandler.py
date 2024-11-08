# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     configHandler
   Description :
   Author :        JHao
   date：          2020/6/22
-------------------------------------------------
   Change Activity:
                   2020/6/22:
-------------------------------------------------
"""
__author__ = 'JHao'

import os
import setting
from util.singleton import Singleton
from util.lazyProperty import LazyProperty
from util.six import reload_six, withMetaclass


class ConfigHandler(withMetaclass(Singleton)):

    def __init__(self):
        pass

    def serverHost(self):
        return setting.HOST

    def serverPort(self):
        return setting.PORT

    @property
    def dbConn(self):
        return os.getenv("DB_CONN", setting.DB_CONN)

    def tableName(self):
        return setting.TABLE_NAME

    @property
    def fetchers(self):
        reload_six(setting)
        return setting.PROXY_FETCHER

    def httpUrl(self):
        return setting.HTTP_URL

    def httpsUrl(self):
        return setting.HTTPS_URL

    def verifyTimeout(self):
        return int(setting.VERIFY_TIMEOUT)

    def maxFailCount(self):
        return int(setting.MAX_FAIL_COUNT)

    def poolSizeMin(self):
        return int(setting.POOL_SIZE_MIN)

    def proxyRegion(self):
        return bool(setting.PROXY_REGION)

    def timezone(self):
        return setting.TIMEZONE

