# -*- coding: UTF-8 -*-


from zh_crawler.topics_generator.id_generator import ZhihuTopicGenerator
from zh_crawler.generator_manager import GeneratorManager
from db.redis_client import redis_cli
import time


def speed_control(gm, ztg):
    '''每分钟检查一次新话题id，尽量保持在300-1000范围内'''
    while True:
        num = redis_cli.scard('zhNewTopicID')
        speed = list(gm.data)[0]
        if num > 1000:
            gm.set_data(ztg.get_hot_topics, speed + 1)
        elif num < 300 and speed > 0:
            gm.data = speed - 1
        time.sleep(60)


def main():
    gm = GeneratorManager()
    ztg = ZhihuTopicGenerator()
    gm.add_generator(ztg.get_hot_topics, 0)
    gm.add_generator(ztg.expand_topics, 0)
    # 自动调整新topicid产生速度
    speed_control(gm, ztg)
