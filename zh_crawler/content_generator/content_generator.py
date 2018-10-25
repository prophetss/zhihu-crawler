# -*- coding: UTF-8 -*-

from util.common import headers, logger
from db.redis_client import redis_cli
from util.decorator import timethis
from bs4 import BeautifulSoup
import requests
import random


@timethis
def crawl_message():
    '''
    知乎精华话题获取,最终结果存放:
    1.zhTopicMessage哈希表内key-话题id，value-字典{'name':名称, 'questions':问题数, 'followers',关注人数}
    2.zhTopicQuestions哈希表key-话题id，value-字典{'question':问题, 'author':作者, 'contents':'评论数':likes':点赞数，‘href':链接}
    '''
    # 知乎精华url
    top_answer_url = 'https://www.zhihu.com/topic/%u/top-answers'
    proxies_list = redis_cli.get_proxies_list()
    tid = redis_cli.block_pop('zhNewTopicID')
    try:
        bf = BeautifulSoup(
            requests.get(url=top_answer_url % int(tid), headers=headers,
                         proxies=random.choice(proxies_list), timeout=3).text, 'html.parser')
        strong = bf.find_all('strong', class_='NumberBoard-itemValue')
        # 0为关注人数，1为问题数
        new_dict = eval(redis_cli.hget('zhTopicMessage', tid))
        new_dict['followers'] = strong[0].get('title')
        new_dict['questions'] = strong[1].get('title')
        redis_cli.hset('zhTopicMessage', tid, new_dict)
        items = bf.find_all('div', class_='ContentItem AnswerItem')
        tqs = []
        for t in items:
            # 问题、作者、评论数、点赞数、链接
            tqs.append(
                {'question': eval(t.get('data-zop'))['title'],
                 'anthor': eval(t.get('data-zop'))['authorName'],
                 'contents': t.find(itemprop='commentCount').get('content'),
                 'likes': t.find('button', class_="Button VoteButton VoteButton--up").contents[-1],
                 'href': t.find('a').get('href')})
        redis_cli.hset('zhTopicQuestions', tid, tqs)
    except Exception as e:
        logger.error(e)


def main():
    while True:
        # 最大速度，其他获取速度以此速度为主
        crawl_message()
