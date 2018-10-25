# -*- coding: utf-8 -*-

import logging
import os

# 通用请求头
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 \
        18  16 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

project_dir = os.path.dirname(os.getcwd())

logger = logging.getLogger()
fh = logging.FileHandler('except.log')
# 相对运行时间ms，文件名行号，线程号，时间，内容信息
fh.setFormatter(
    logging.Formatter('%(relativeCreated)d %(filename)s%(lineno)d %(thread)s %(asctime)s %(message)s'))
logger.addHandler(fh)
