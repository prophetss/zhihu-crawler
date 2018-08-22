# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
import requests
import random
import common
import time


def crawl_message():
    # 知乎精华url
    start = time.clock()
    top_answer_url = 'https://www.zhihu.com/topic/%u/top-answers'
    proxies_list = common.get_proxies_list()
    with requests.Session() as s:
        for tid in common.r.hkeys('zhNewTopicName'):
            try:
                bf = BeautifulSoup(
                    s.get(url=top_answer_url % int(tid), headers=common.HEADERS,
                          proxies=random.choice(proxies_list), timeout=3).text, 'html.parser')
                strong = bf.find_all('strong', class_='NumberBoard-itemValue')
                # 0为关注人数，1为问题数
                common.r.hset('zhTopicMessage', tid, (strong[0].get('title'), strong[1].get('title')))
                items = bf.find_all('div', class_='ContentItem AnswerItem')
                tqs = []
                for t in items:
                    # 问题、作者、评论数、点赞数、链接
                    tqs.append((eval(t.get('data-zop'))['title'], eval(t.get('data-zop'))['authorName'],
                                t.find(itemprop='commentCount').get('content'),
                                t.find('button', class_="Button VoteButton VoteButton--up").contents[-1],
                                t.find('a').get('href')))
                common.r.hset('zhTopicQuestions', tid, tqs)
                time.sleep(0.2)
            except Exception as e:
                common.error_print(e)
    print('Running zhihu_message_crawl time: %.2f Seconds\n' % (time.clock() - start))


print(common.r.hlen('zhTopicQuestions'))
