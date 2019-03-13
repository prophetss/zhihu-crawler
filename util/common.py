# -*- coding: utf-8 -*-

import logging
import os

# 通用请求头
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 \
        18  16 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def addtwodimdict(thedict, key_a, key_b, val):
    if key_a in thedict:
        thedict[key_a][key_b] = val
    else:
        thedict[key_a] = {key_b: val}


def error_print(string):
    print("\033[1;31;0m{}\033[0m".format(string))
