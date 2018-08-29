# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
import requests
import random
import common
import time

'''
知乎精华话题获取,最终结果存放:
1.zhTopicMessage哈希表内key-话题id，value-字典{'name':名称, 'questions':问题数, 'followers',关注人数} 
2.zhTopicQuestions哈希表key-话题id，value-字典{'question':问题, 'author':作者, 'contents':'评论数':likes':点赞数，‘href':链接} 
'''


@common.running_time
def crawl_message():
    # 知乎精华url
    top_answer_url = 'https://www.zhihu.com/topic/%u/top-answers'
    proxies_list = common.get_proxies_list()
    with requests.Session() as s:
        for tid in common.r.smembers('zhNewTopicID'):
            try:
                bf = BeautifulSoup(
                    s.get(url=top_answer_url % int(tid), headers=common.HEADERS,
                          proxies=random.choice(proxies_list), timeout=3).text, 'html.parser')
                strong = bf.find_all('strong', class_='NumberBoard-itemValue')
                # 0为关注人数，1为问题数
                new_dict = eval(common.r.hget('zhTopicMessage', tid))
                new_dict['followers'] = strong[0].get('title')
                new_dict['questions'] = strong[1].get('title')
                common.r.hset('zhTopicMessage', tid, new_dict)
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
                common.r.hset('zhTopicQuestions', tid, tqs)
                time.sleep(common.sleep_time)
            except Exception as e:
                common.error_print(e)
