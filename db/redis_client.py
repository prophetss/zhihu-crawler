# -*- coding: utf-8 -*-

from util.config import conf
import redis
import time


class RedisClient(redis.Redis):

    def __init__(self):
        super().__init__(connection_pool=redis.ConnectionPool(host=conf.db_redis_host, port=conf.db_redis_port,
                                                              db=conf.db_redis_name))
        # 设置获取的关键词生存期为一天,一天有效期内不重复保留
        super().expire('zhKeyWords', 86400)
        # 设置话题的生存期为30天，一个周期后话题重新抓取相应信息
        super().expire('zhTopicMessage', 2592000)

    def get_proxies_list(self):
        '''需运行https://github.com/jhao104/proxy_pool此程序'''
        ups = []
        for ip in super().hkeys('useful_proxy'):
            ups.append({'http': ip})
        return ups

    def save_keyword(self, kw):
        '''新待搜索关键词结果存入zhTemporaryWords表中'''
        if super().sadd('zhKeyWords', kw):
            # 添加未发生覆盖，将此关键词存至zhTemporaryWords内待被搜索
            super().sadd('zhTemporaryWords', kw)

    def block_pop(self, key):
        '''模拟阻塞获取集合内元素'''
        while True:
            elem = super().spop(key)
            if elem:
                return elem
            else:
                time.sleep(1)


redis_cli = RedisClient()
