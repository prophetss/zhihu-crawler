# -*- coding: UTF-8 -*-


import requests
import random
import common
import time
import json

'''
知乎话题获取,最终结果存放:
1.zhTopicMessage哈希表内key-话题id，value-字典{'name':名称, 'questions':问题数, 'followers',关注人数} 
2.zhTopicDAG内key-父话题id，value-子话题id队列
'''

# 设置话题的生存期为30天，一个周期后话题重新抓取
common.r.expire('zhTopicMessage', 2592000)

new_topic_ids = {}


def save_topic(topic_id, topic_name):
    if not common.r.hexists('zhTopicMessage', topic_id):
        # 新话题存至new_topic_ids内待被扩展
        print(topic_name)
        new_topic_ids[topic_id] = topic_name


@common.running_time
def get_hot_topics():
    # 清空新话题
    common.r.delete('zhNewTopicID')
    zh_search_url = 'https://www.zhihu.com/api/v4/search_v3?t=topic&q=%s&correction=1&offset=%d&limit=10'
    # 需运行https://github.com/jhao104/proxy_pool此程序抓取免费代理ip，也可替换get_proxies_list1简单从一个固定
    # 网站抓取，再或者可以自行获取
    proxies_list = common.get_proxies_list()
    with requests.Session() as s:
        for tw in common.r.smembers('zhTemporaryWords'):
            offset = 0
            # 不断翻页至最后
            while True:
                # 每一页获取话题名称和id
                try:
                    topics = json.loads(s.get(url=zh_search_url % (tw, offset), headers=common.HEADERS,
                                              proxies=random.choice(proxies_list), timeout=3).text)['data']
                    if not topics:
                        break
                    for t in topics:
                        save_topic(t['object']['id'],
                                   str(t['highlight']['title']).replace('<em>', '').replace('</em>', ''))
                    time.sleep(common.sleep_time)
                    offset += 10
                except Exception as e:
                    common.error_print(e)
                    continue


def save_to_dag(child_topic_id, parent_topic_id):
    ids = common.r.hget('zhTopicDAG', parent_topic_id)
    if ids:
        new_ids = eval(ids)
        new_ids.add(child_topic_id)
        common.r.hset('zhTopicDAG', parent_topic_id, new_ids)
    else:
        common.r.hset('zhTopicDAG', parent_topic_id, {child_topic_id})
    return common.r.hexists('zhTopicMessage', parent_topic_id)


def add_topics(url, topic_id, func):
    try:
        for p in json.loads(requests.get(url=url % int(topic_id), headers=common.HEADERS,
                                         proxies=random.choice(add_topics.proxies_list), timeout=3).text)['data']:
            expand_topic_id = int(p['id'])
            if not func(topic_id, expand_topic_id):
                new_topic_ids[expand_topic_id] = p['name']
        time.sleep(common.sleep_time)
    except Exception as e:
        common.error_print(e)


@common.running_time
def expand_topics():
    '话题扩展，分别向父子话题不断扩展'
    add_topics.proxies_list = common.get_proxies_list()
    parent_url = 'https://www.zhihu.com/api/v3/topics/%d/parent'
    child_url = 'https://www.zhihu.com/api/v3/topics/%d/child'
    while new_topic_ids:
        topic = new_topic_ids.popitem()
        add_topics(parent_url, topic[0], lambda a, b: save_to_dag(a, b))
        add_topics(child_url, topic[0], lambda a, b: save_to_dag(b, a))
        if not common.r.hexists('zhTopicMessage', topic[0]):
            print(topic[1])
            common.r.hset('zhTopicMessage', topic[0], {'name': topic[1]})
        common.r.sadd('zhNewTopicID', topic[0])
