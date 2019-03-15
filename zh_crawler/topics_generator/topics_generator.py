from requests.exceptions import RequestException
from requests.exceptions import ReadTimeout
from requests.adapters import HTTPAdapter
from db.redis_client import redis_cli
from util.common import headers
from util.loghandler import LogHandler
from urllib3.util.retry import Retry
from util.decorator import timethis
from util.config import conf
import logging
import requests
import random
import queue
import time

"""
知乎话题获取,最终结果存放:
1.话题信息：zhTopicMessage哈希表内，key-话题id，value-{'name':名称, 'introduction': 简介, 'questions':问题数,
'top_answers':精华问题数, 'followers':关注人数, 'best_answerers':优秀回答者人数}
2.话题结构：zhTopicDAG内，key-父话题id，value-子话题id队列
"""


class ZhihuTopicGenerator:
    """ 分为两个过程:id获取和扩展 """

    topic_message_url = 'https://www.zhihu.com/api/v3/topics/%u'  # 话题信息
    zh_search_url = 'https://www.zhihu.com/api/v4/search_v3?t=topic&q=%s&correction=1&offset=%d&limit=10'  # 问题搜索
    parent_url = 'https://www.zhihu.com/api/v3/topics/%d/parent'  # 父话题api
    child_url = 'https://www.zhihu.com/api/v3/topics/%d/child'  # 子话题api

    def __init__(self):
        # 代理ip
        self.proxies_list = []
        # 待扩展队列
        self.__id_queue = queue.Queue()
        # 建立会话，设置requests重连次数和重连等待时间
        self.session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.logger = LogHandler('topics_generator')
        logging.getLogger("urllib3").setLevel(logging.ERROR)

    def __get_topic_message(self, tid):
        """
        话题信息获取,最终结果存放:
        zhTopicMessage哈希表内，key-话题id，value-{'name':名称, 'introduction': 简介, 'questions_count':问题数,
        'best_answers_count':精华问题数, 'followers_count':关注人数, 'best_answerers_count':优秀回答者人数}
        """
        try:
            j_rst = self.session.get(url=ZhihuTopicGenerator.topic_message_url % tid, headers=headers,
                                     proxies=random.choice(self.proxies_list), timeout=0.1).json()
            if redis_cli.hset('zhTopicMessage', tid,
                              str({"name": j_rst.get("name"), 'introduction': j_rst.get("introduction"),
                                   "questions_count": j_rst.get("questions_count"),
                                   "best_answers_count": j_rst.get("best_answers_count"),
                                   'followers_count': j_rst.get("followers_count"),
                                   "best_answerers_count": j_rst.get("best_answerers_count")})):
                # 新话题存至__id_queue内待被扩展
                self.__id_queue.put(tid)
                # 待获取相关信息
                redis_cli.sadd('zhNewTopicID', tid)
        except RequestException as re:
            self.logger.warn(re)
        except Exception as e:
            raise e

    def __get_hot_topics(self):
        """ 搜索zhTemporaryWords内关键词，从其结果中得到相关话题id和名称 """
        tw = redis_cli.block_pop('zhTemporaryWords').decode('utf-8')  # pop
        # 不断翻页至最后,最大获取1000条
        for offset in range(0, 1000, 10):
            try:
                url = ZhihuTopicGenerator.zh_search_url % (tw, offset)
                topics = self.session.get(url=url, headers=headers,
                                          proxies=random.choice(self.proxies_list), timeout=3).json().get('data')
                if not topics:  # 已到最后
                    return
                # 每一页获取话题相关详细信息
                for t in topics:
                    if t.get('object') and t.get('object').get('id'):
                        try:
                            tid = int(t['object']['id'])
                        except ValueError as ve:
                            self.logger.warn(ve, t['object']['id'])
                        self.__get_topic_message(tid)
                    else:
                        break
            except RequestException as re:
                self.logger.warn(re, url)
            except ReadTimeout as rte:
                self.logger.warn(rte, url)
            except KeyError as ke:
                self.logger.warn(ke, url)
            except Exception as e:
                raise e

    @staticmethod
    def __save_to_dag(child_topic_id, parent_topic_id):
        """ 按其结构保存为有向无环图 """
        ids = redis_cli.hget('zhTopicDAG', parent_topic_id)
        if not ids or ids.decode() == "None":
            redis_cli.hset('zhTopicDAG', parent_topic_id, str({child_topic_id}))
        else:
            new_ids = eval(ids)
            new_ids.add(child_topic_id)
            redis_cli.hset('zhTopicDAG', parent_topic_id, str(new_ids))

    def __add_topics(self, url, topic_id, func):
        try:
            req = self.session.get(url=url % int(topic_id), headers=headers,
                                   proxies=random.choice(self.proxies_list), timeout=3)
            if not req:  # 获取子父话题有可能不存在
                return
            for p in req.json()['data']:
                expand_topic_id = int(p['id'])
                func(topic_id, expand_topic_id)
                self.__get_topic_message(expand_topic_id)
        except RequestException as re:
            self.logger.warn(re)
        except ReadTimeout as rte:
            self.logger.warn(rte)
        except Exception as e:
            raise e

    def __expand_topics(self):
        """ 话题扩展，分别向父子话题不断扩展 """
        topic = self.__id_queue.get()
        self.__add_topics(ZhihuTopicGenerator.parent_url, topic, lambda a, b: self.__save_to_dag(a, b))
        self.__add_topics(ZhihuTopicGenerator.child_url, topic, lambda a, b: self.__save_to_dag(b, a))

    @timethis
    def process(self):
        self.proxies_list = redis_cli.get_proxies_list()
        self.__get_hot_topics()
        while not self.__id_queue.empty():
            self.__expand_topics()


def speed_state(threshold):
    return redis_cli.scard('zhNewTopicID') < threshold




def run():
    """ 获取话题id和其主要信息 """
    ztg = ZhihuTopicGenerator()
    mode_control = {1: True, 2: False, 3: True, 4: speed_state(5)}  # 模式控制
    while True:
        if mode_control[conf.option] and redis_cli.proxy_ip_detect():
            ztg.process()
        else:
            time.sleep(3)


if __name__ == '__main__':
    run()
