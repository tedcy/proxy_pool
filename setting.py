# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     setting.py
   Description :   配置文件
   Author :        JHao
   date：          2019/2/15
-------------------------------------------------
   Change Activity:
                   2019/2/15:
-------------------------------------------------
"""

BANNER = r"""
****************************************************************
*** ______  ********************* ______ *********** _  ********
*** | ___ \_ ******************** | ___ \ ********* | | ********
*** | |_/ / \__ __   __  _ __   _ | |_/ /___ * ___  | | ********
*** |  __/|  _// _ \ \ \/ /| | | ||  __// _ \ / _ \ | | ********
*** | |   | | | (_) | >  < \ |_| || |  | (_) | (_) || |___  ****
*** \_|   |_|  \___/ /_/\_\ \__  |\_|   \___/ \___/ \_____/ ****
****                       __ / /                          *****
************************* /___ / *******************************
*************************       ********************************
****************************************************************
"""

VERSION = "2.4.0"

# ############### server config ###############
HOST = "0.0.0.0"

PORT = 5010

# ############### database config ###################
# db connection uri
# example:
#      Redis: redis://:password@ip:port/db
#      Ssdb:  ssdb://:password@ip:port
DB_CONN = 'redis://:pwd@127.0.0.1:6379/0'

# proxy table name
TABLE_NAME = 'use_proxy'


# ###### config the proxy fetch function ######
PROXY_FETCHER = [
    "freeProxy01",
    "freeProxy02",
    "freeProxy03",
    "freeProxy04",
    "freeProxy05",
]

# ############# proxy validator #################
# 代理验证目标网站
HTTP_URL = "http://www.baidu.com"

HTTPS_URL = "https://www.baidu.com"

# 代理验证时超时时间
VERIFY_TIMEOUT = 3

# 允许的最大失败次数,超过则剔除代理
MAX_FAIL_COUNT = 1

# proxyCheck时代理数量少于POOL_SIZE_MIN触发抓取
POOL_SIZE_MIN = 100

# ############# proxy attributes #################
# 是否启用代理地域属性
PROXY_REGION = True

# ############# scheduler config #################

# Set the timezone for the scheduler forcely (optional)
# If it is running on a VM, and
#   "ValueError: Timezone offset does not match system offset"
#   was raised during scheduling.
# Please uncomment the following line and set a timezone for the scheduler.
# Otherwise it will detect the timezone from the system automatically.

TIMEZONE = "Asia/Shanghai"

import time
import threading
import setting
from handler.logHandler import LogHandler

log = LogHandler('setting')

def read_and_apply_config(file_path):
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.strip():
                    key, value = line.strip().split('=', 1)
                    if key == 'POOL_SIZE_MIN':
                        setting.POOL_SIZE_MIN = int(value)
                        log.info(f"POOL_SIZE_MIN has been set to {setting.POOL_SIZE_MIN}")
                    if key == 'VERIFY_TIMEOUT':
                        setting.VERIFY_TIMEOUT = int(value)
                        log.info(f"VERIFY_TIMEOUT has been set to {setting.VERIFY_TIMEOUT}")
                    if key == 'MAX_FAIL_COUNT':
                        setting.MAX_FAIL_COUNT = int(value)
                        log.info(f"MAX_FAIL_COUNT has been set to {setting.MAX_FAIL_COUNT}")
    except Exception as e:
        log.info(f"An error occurred while reading the file: {e}")

def periodic_file_reader():
    file_path = "setting.conf"
    def _reader():
        while True:
            read_and_apply_config(file_path)
            time.sleep(10)

    reader_thread = threading.Thread(target=_reader, daemon=True)
    reader_thread.start()
