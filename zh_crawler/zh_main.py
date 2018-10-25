# -*- coding: utf-8 -*-

from zh_crawler.keywords_generator.keywords_controller import main as kw_run
from zh_crawler.content_generator.content_generator import main as ct_run
from zh_crawler.topics_generator.topics_controller import main as tp_run
from db.redis_client import redis_cli
from multiprocessing import Process
import time


def main():
    # 获取关键词
    p1 = Process(target=kw_run, name='kw_run', args=())
    # 获取话题
    p2 = Process(target=tp_run, name='tp_run', args=())
    # 获取话题对应内容
    p3 = Process(target=ct_run, name='ct_run', args=())
    p1.start()
    p2.start()
    p3.start()

    '''
    状态监控，显示抓取到数量，
    zhTemporaryWords：新待搜索关键词
    zhTopicMessage：总话题结果信息
    zhNewTopicID：搜索后获取到的新话题id
    zhTopicQuestions：话题精华问题等相关内容
    '''
    while True:
        print('\rzhTemporaryWords:%d    zhTopicMessage:%d     zhNewTopicID:%d   zhTopicQuestions:%d' % (
            redis_cli.scard('zhTemporaryWords'), redis_cli.hlen('zhTopicMessage'), redis_cli.scard('zhNewTopicID'),
            redis_cli.hlen('zhTopicQuestions')), end='')
        time.sleep(5)
