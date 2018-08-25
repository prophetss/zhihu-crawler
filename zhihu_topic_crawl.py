# -*- coding: UTF-8 -*-

import requests
import random
import common
import queue
import time
import json

'''
知乎话题获取,最终结果存放：1.zhTopicName哈希表内key-话题id，value-名称
2.zhTopicDAG内key-父话题id，value-子话题id队列
'''

# 设置话题的生存期为30天
common.r.expire('zhTopicName', 2592000)


def save_topic(topic_id, topic_name):
    if common.r.hset('zhTopicName', topic_id, topic_name):
        # 添加未发生覆盖，将此话题存至zhNewTopicName内待被扩展
        print(topic_name)
        common.r.hset('zhNewTopicName', topic_id, topic_name)


def get_hot_topics():
    # 清空新话题
    common.r.delete('zhNewTopicName')
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
                    time.sleep(0.2)
                    offset += 10
                except Exception as e:
                    common.error_print(e)
                    continue


# 当前只向父话题不断查询扩充
def expand_topics():
    proxies_list = common.get_proxies_list()
    parent_url = 'https://www.zhihu.com/api/v3/topics/%d/parent'
    for tid in common.r.hkeys('zhNewTopicName'):
        parent_topic_ids = queue.Queue()
        parent_topic_ids.put(tid)
        while not parent_topic_ids.empty():
            child_topic_id = parent_topic_ids.get()
            try:
                for p in json.loads(requests.get(url=parent_url % int(child_topic_id), headers=common.HEADERS,
                                                 proxies=random.choice(proxies_list), timeout=3).text)['data']:
                    parent_topic_name = p['name']
                    parent_topic_id = int(p['id'])
                    ids = common.r.hget('zhTopicDAG', parent_topic_id)
                    if ids:
						newset = eval(ids)
                        newset.add(child_topic_id)
						common.r.hset('zhTopicDAG', parent_topic_id, newset)
                    else:
                        parent_topic_ids.put(parent_topic_id)
                        common.r.hset('zhTopicDAG', parent_topic_id, {tid})
                        save_topic(parent_topic_id, parent_topic_name)
                time.sleep(0.2)
            except Exception as e:
                common.error_print(e)
