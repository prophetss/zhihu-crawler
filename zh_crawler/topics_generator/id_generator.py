# -*- coding: UTF-8 -*-

from db.redis_client import redis_cli
from util.common import headers, logger
from util.decorator import timethis
import requests
import random
import queue
import time
import json

'''
知乎话题获取,最终结果存放:
1.zhTopicMessage哈希表内key-话题id，value-字典{'name':名称, 'questions':问题数, 'followers',关注人数} 
2.zhTopicDAG内key-父话题id，value-子话题id队列
'''


class ZhihuTopicGenerator:

    def __init__(self):
        self.id_queue = queue.Queue()

    def save_topic(self, topic_id, topic_name):
        if not redis_cli.hexists('zhTopicMessage', topic_id):
            redis_cli.hset('zhTopicMessage', topic_id, {'name': topic_name})
            # 新话题存至id_queue内待被扩展
            self.id_queue.put((topic_id, topic_name))
            # 待获取相关信息
            redis_cli.sadd('zhNewTopicID', topic_id)

    @timethis
    def get_hot_topics(self, sleep_time):
        '''搜索zhTemporaryWords内关键词，从其结果中得到相关话题id和名称'''
        proxies_list = redis_cli.get_proxies_list()
        zh_search_url = 'https://www.zhihu.com/api/v4/search_v3?t=topic&q=%s&correction=1&offset=%d&limit=10'
        tw = redis_cli.block_pop('zhTemporaryWords').decode('utf-8')  # 阻塞pop
        with requests.Session() as s:
            try:
                offset = 0
                while True:
                    # 不断翻页至最后
                    topics = json.loads(s.get(url=zh_search_url % (tw, offset), headers=headers,
                                              proxies=random.choice(proxies_list),
                                              timeout=3).text)['data']
                    if not topics:
                        return
                    # 每一页获取话题名称和id
                    for t in topics:
                        self.save_topic(t['object']['id'],
                                        str(t['highlight']['title']).replace('<em>', '').replace(
                                            '</em>', ''))
                    offset += 10
            except Exception as e:
                logger.error(e)
        time.sleep(sleep_time)

    def __add_topics(self, url, topic_id, func):
        proxies_list = redis_cli.get_proxies_list()
        try:
            for p in json.loads(requests.get(url=url % int(topic_id), headers=headers,
                                             proxies=random.choice(proxies_list), timeout=3).text)['data']:
                expand_topic_id = int(p['id'])
                func(topic_id, expand_topic_id)
                self.save_topic(expand_topic_id, p['name'])
        except Exception as e:
            logger.error(e)

    def expand_topics(self, sleep_time):
        '话题扩展，分别向父子话题不断扩展'
        parent_url = 'https://www.zhihu.com/api/v3/topics/%d/parent'
        child_url = 'https://www.zhihu.com/api/v3/topics/%d/child'
        topic = self.id_queue.get()
        self.__add_topics(parent_url, topic[0], lambda a, b: ZhihuTopicGenerator.save_to_dag(a, b))
        self.__add_topics(child_url, topic[0], lambda a, b: ZhihuTopicGenerator.save_to_dag(b, a))
        time.sleep(sleep_time)

    @staticmethod
    def save_to_dag(child_topic_id, parent_topic_id):
        ids = redis_cli.hget('zhTopicDAG', parent_topic_id)
        if ids:
            new_ids = eval(ids)
            new_ids.add(child_topic_id)
            redis_cli.hset('zhTopicDAG', parent_topic_id, new_ids)
        else:
            redis_cli.hset('zhTopicDAG', parent_topic_id, {child_topic_id})
