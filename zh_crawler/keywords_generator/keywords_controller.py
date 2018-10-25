# -*- coding: utf-8 -*-

''''''

from zh_crawler.keywords_generator.baiduhot_generator import BaiduHotGenerator
from zh_crawler.keywords_generator.zhidao_generator import ZhiDaoGenerator
from zh_crawler.generator_manager import GeneratorManager
from db.redis_client import redis_cli
import time


def speed_control(gm):
    '''每分钟检查一次新关键词数量，尽量保持在500-1000范围内'''
    while True:
        num = redis_cli.scard('zhTemporaryWords')
        speed = list(gm.data)[0]
        if num > 1000:
            gm.data = speed + 1
        elif num < 500 and speed > 0:
            gm.data = speed - 1
        time.sleep(60)


def main():
    '''所有新关键词存至zhTemporaryWords内待被搜索'''
    gm = GeneratorManager()
    # 起始速度设置0最大
    gm.add_generator(ZhiDaoGenerator().crawl_zhidao_words, 0)
    gm.add_generator(BaiduHotGenerator().crawl_hot_words, 0)
    # 自动调整新关键词获取速度
    speed_control(gm)
