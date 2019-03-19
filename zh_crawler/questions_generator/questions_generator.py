from db.redis_client import redis_cli
from util.common import headers
from util.common import addtwodimdict
from util.loghandler import LogHandler
from util.config import conf
from util.common import PROJECT_DIR
from util.decorator import timethis
from json.decoder import JSONDecodeError
import requests
import random
import time
import json
import os

OUTPUT_PATH = os.path.join(PROJECT_DIR, 'output')


class QuestionsGenerator:
    """ 获取话题内的精华和讨论问题"""
    top_activity_url = "https://www.zhihu.com/api/v4/topics/%u/feeds/top_activity?limit=10&offset=%u"  # 讨论问题
    essence_url = "https://www.zhihu.com/api/v4/topics/%u/feeds/essence?limit=10&offset=%u"  # 精华问题

    def __init__(self):
        self.proxies_list = []
        self.essence_dict = dict()
        self.activity_dict = dict()
        self.session = requests.Session()
        self.logger = LogHandler("question_generator")

    @staticmethod
    def badge_parse(badge):
        res_array = []
        for b in badge:
            res_array.append({'author_type': b['type'], 'author_description': b['description']})
        return res_array

    def topic_sticky_parse(self, topic_sticky):
        res_array = []
        try:
            for t in topic_sticky:
                if t['target'].get('title'):
                    res_array.append({'id': t['target']['id'],
                                      'title': t['target']['title'],
                                      'author_name': t['target']['author']['name'],
                                      'author_gender': t['target']['author']['gender'],
                                      'author_headline': t['target']['author']['headline'],
                                      'author_url_token': t['target']['author']['url_token'],
                                      'excerpt': t['target']['excerpt'],
                                      'updated_time': t['target']['updated'],
                                      'contents': t['target']['comment_count'],
                                      'likes': t['target']['voteup_count'],
                                      'created_time': t['target']['created']})
                else:
                    res_array.append({'id': t['target']['id'],  # 热门回答
                                      'title': t['target']['question']['title'],
                                      'author_name': t['target']['author']['name'],
                                      'author_gender': t['target']['author']['gender'],
                                      'author_headline': t['target']['author']['headline'],
                                      'author_url_token': t['target']['author']['url_token'],
                                      'excerpt': t['target']['excerpt'],
                                      'updated_time': t['target']['updated_time'],
                                      'created': t['target']['question']['created'],
                                      'created_time': t['target']['created_time']})
        except KeyError as ke:
            self.logger.error(ke, topic_sticky)
        except Exception as e:
            raise e
        return res_array

    @timethis
    def crawl_topic_message(self, tid, q_url, num, message_dict):
        """
        话题对应问题/文章获取,最终结果存放:
        message_dict: key-类型（文章/问题），value-{key-id, value-{'question/title':问题/文章名称, author':作者,
        'gender':性别,'author_badge':作者标签, 'author_headline':作者签名, 'author_url_token':作者url标识，excerpt':摘录，
        'created_time':创建时间, 'updated_time':最后更新时间, 'comment_count':'评论数', likes':点赞数}}
        :param tid:话题ID
        :param q_url:请求url
        :param num 抓取数量
        :param message_dict:存储字典
        :return:
        """
        self.proxies_list = redis_cli.get_proxies_list()
        session = requests.session()
        sticky_num = 0
        for offset in range(0, num, 10):
            url = q_url % (tid, offset)
            try:
                ques = session.get(url=url, headers=headers,
                                   proxies=random.choice(self.proxies_list),
                                   timeout=3)
            except Exception as re:
                self.logger.warn((re, url))
                continue
            try:
                q_json = ques.json() if ques else {}
            except JSONDecodeError as je:
                self.logger.error((je, url, ques))
                continue
            for q in q_json.get('data', []):
                target = q.get('target', {})
                question_type = str(target.get('type', 'none_type')).lower()
                if question_type == 'none_type':
                    continue
                elif question_type == 'answer':
                    # 问题回答是双id,使用元组转成字符串
                    addtwodimdict(message_dict, 'answer', str((target['question']['id'], target['id'])),
                                  {'question': target['question']['title'],
                                   'author_name': target['author']['name'],
                                   'author_gender': target['author']['gender'],
                                   'author_badge': QuestionsGenerator.badge_parse(target['author']['badge']),
                                   'author_headline': target['author']['headline'],
                                   'author_url_token': target['author']['url_token'],
                                   'excerpt': target['excerpt'], 'created_time': target['created_time'],
                                   'updated_time': target['updated_time'], 'contents': target['comment_count'],
                                   'likes': target['voteup_count']})
                elif question_type == 'article':
                    # 文章是单id
                    addtwodimdict(message_dict, 'article', target['id'],
                                  {'title': target['title'],
                                   'author_name': target['author']['name'],
                                   'author_gender': target['author']['gender'],
                                   'author_badge': QuestionsGenerator.badge_parse(target['author']['badge']),
                                   'author_headline': target['author']['headline'],
                                   'author_url_token': target['author']['url_token'],
                                   'excerpt': target['excerpt'], 'created_time': target['created'],
                                   'updated_time': target['updated'], 'contents': target['comment_count'],
                                   'likes': target['voteup_count']})
                elif question_type == 'question':
                    pass  # 目前抓取到的是一些没有回答的问题，这里过滤掉
                elif question_type == 'topic_sticky_module':  # 热门置顶
                    addtwodimdict(message_dict, 'topic_sticky_module', sticky_num,
                                  {'title': target['title'],
                                   'data': self.topic_sticky_parse(target['data'])})
                    sticky_num += 1
                else:
                    self.logger.error("There was a new type:{}!\n".format(question_type))
            if str(q_json.get('paging', {}).get('is_end', 'none')).lower() == 'true':
                return

    def run(self):
        """
        zhTopicQuestions内包含精华(点赞比较多)和讨论(最新比较热)的问题和文章
        对应结构essence_dict和activity_dict
        :return:
        """
        tid = int(redis_cli.block_pop('zhNewTopicID'))
        self.crawl_topic_message(tid, QuestionsGenerator.essence_url, conf.essence_nums, self.essence_dict)
        self.crawl_topic_message(tid, QuestionsGenerator.top_activity_url, conf.top_activity_nums, self.activity_dict)
        with open(os.path.join(OUTPUT_PATH, "{}.json".format(int(tid))), "w", encoding="GB18030") as f:
            json.dump({'essence': self.essence_dict, 'top_activity': self.activity_dict}, f, indent=4,
                      ensure_ascii=False)


def save_new_topic_id():
    """ output目录下不要手动放其他名称文件 """
    for nid in set(redis_cli.hkeys('zhTopicMessage')) - set({x.split('.')[0] for x in os.listdir(OUTPUT_PATH)}):
        redis_cli.sadd('zhNewTopicID', nid)


def run():
    """ 结果以json文件存至output目录下，文件名为话题id """
    # 先从话题id中筛选出未获取问题的id放入待获取队列
    save_new_topic_id()
    qg = QuestionsGenerator()
    while True:
        # 不控制速度
        if redis_cli.proxy_ip_detect():
            qg.run()
        else:
            time.sleep(3)


if __name__ == '__main__':
    run()
