from util.decorator import singleton
from util.config import conf
import redis
import time


@singleton
class CrawlerDBClient(redis.Redis):
    def __init__(self, host='localhost', port=6379, db=0):
        super().__init__(connection_pool=redis.ConnectionPool(host=host, port=port, db=db))
        super().expire('zhKeyWords', conf.db_keyword_life_cycle * 86400)  # 设置待搜索关键词生存期，一个周期后重新抓取
        super().expire('zhTopicMessage', conf.db_topic_life_cycle * 86400)  # 设置话题生存期，一个周期后话题重新抓取相应信息

    def block_pop(self, key):
        """ 模拟阻塞获取集合内元素 """
        while True:
            elem = super().spop(key)
            if elem:
                return elem
            else:
                time.sleep(1)


redis_cli = CrawlerDBClient()
