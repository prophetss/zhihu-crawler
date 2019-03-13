from zh_crawler.keywords_generator.baiduhot_generator import BaiduHotGenerator
from zh_crawler.keywords_generator.zhidao_generator import ZhiDaoGenerator
from util.loghandler import LogHandler
from db.redis_client import redis_cli
import time


class KeywordsController:
    """ 获取待搜索关键词 """

    def __init__(self):
        self.sleep_time = 0
        self.zdg = ZhiDaoGenerator()
        self.bhg = BaiduHotGenerator()
        self.logger = LogHandler('keywords_controller')

    def speed_control(self):
        """ 检查一次新关键词数量，控制在500-1000范围内 """
        nums = redis_cli.scard('zhTemporaryWords')
        if nums > 1000:  # 多一些可以接受，所以缓慢增加睡眠时间
            self.sleep_time += 10
        elif nums < 500:  # 过少时迅速降低睡眠时间防止饥饿
            self.sleep_time = int(self.sleep_time / 2)
        self.logger.info('keywords crawler sleep time:%d\n' % self.sleep_time)
        time.sleep(self.sleep_time)

    def get_words(self):
        self.zdg.crawl_zhidao_words()
        self.bhg.crawl_hot_words()

    def kw_run(self):
        """ 所有新关键词存至zhTemporaryWords内待被搜索 """
        actions = [self.get_words] * 10 + [self.speed_control]  # 每十次检测一次速度
        while True:
            for action in actions:
                action()


def run():
    KeywordsController().kw_run()
