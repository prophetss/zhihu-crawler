from zh_crawler.keywords_generator.baiduhot_generator import BaiduHotGenerator
from zh_crawler.keywords_generator.zhidao_generator import ZhiDaoGenerator
from util.loghandler import LogHandler
from db.crawler.crawler_db_client import redis_cli
import time


class KeywordsController:
    """ 获取待搜索关键词 """

    def __init__(self):
        self.sleep_time = 0
        self.task_list = [ZhiDaoGenerator().crawl_zhidao_words, BaiduHotGenerator().crawl_hot_words]
        self.logger = LogHandler('keywords_controller')

    def speed_control(self, kw):
        """ 检查一次新关键词数量，控制在500-1000范围内 """
        nums = redis_cli.scard('zhTemporaryWords')
        if nums > 1000:  # 多一些可以接受，所以缓慢增加睡眠时间
            self.sleep_time += 10
        elif nums < 500:  # 过少时迅速降低睡眠时间防止饥饿
            self.sleep_time = int(self.sleep_time / 2)
        self.logger.info('keywords crawler sleep time:%d' % self.sleep_time)
        time.sleep(self.sleep_time)

    def save_keyword(self, kw):
        """ 新待搜索关键词结果存入zhTemporaryWords表中 """
        if redis_cli.sadd('zhKeyWords', kw):
            # 添加未发生覆盖，将此关键词存至zhTemporaryWords内待被搜索
            self.logger.info(str(kw))
            redis_cli.sadd('zhTemporaryWords', kw)

    def kw_run(self):
        """ 所有新关键词存至zhTemporaryWords内待被搜索 """
        while True:
            # 每5次更新一次速度
            for action in self.task_list * 5 + [self.speed_control]:
                action(self.save_keyword)


def run():
    KeywordsController().kw_run()


if __name__ == '__main__':
    run()
