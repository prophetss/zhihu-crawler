# -*- coding: utf-8 -*-

from util.decorator import singleton
from util.common import error_print
from util.config import conf
import redis
import time


@singleton
class RedisClient(redis.Redis):

    def __init__(self):
        super().__init__(connection_pool=redis.ConnectionPool(host=conf.db_redis_host, port=conf.db_redis_port,
                                                              db=conf.db_redis_name))
        self.proxy_ip_cursor = 0  # 代理ip获取游标
        # super().expire('zhKeyWords', 86400)  # 设置获取的关键词生存期为一天,一天有效期内不重复保留
        # super().expire('zhTopicMessage', 2592000)  # 设置话题的生存期为30天，一个周期后话题重新抓取相应信息

    def get_proxies_list(self):
        """ 一次获取适量代理ip """
        ip_list = []
        count = 10
        while count != 0:
            self.proxy_ip_cursor, ips = super().hscan('useful_proxy', cursor=self.proxy_ip_cursor, count=50)
            for ip in dict(ips).keys():
                ip_list.append({'http': ip})
            if ip_list:
                return ip_list
            time.sleep(10)
            count -= 1
        raise Exception("ERROR: Proxy IP List Is None!")

    def save_keyword(self, kw):
        """ 新待搜索关键词结果存入zhTemporaryWords表中 """
        if super().sadd('zhKeyWords', kw):
            # 添加未发生覆盖，将此关键词存至zhTemporaryWords内待被搜索
            super().sadd('zhTemporaryWords', kw)

    def block_pop(self, key):
        """ 模拟阻塞获取集合内元素 """
        while True:
            elem = super().spop(key)
            if elem:
                return elem
            else:
                time.sleep(1)

    def proxy_ip_detect(self):
        return self.hlen('useful_proxy') > 5


redis_cli = RedisClient()
