from apscheduler.schedulers.background import BackgroundScheduler
from db.crawler.crawler_db_client import redis_cli
import logging
import time
import datetime
import random


class ProxiesReceiver:
    def __init__(self):
        self.proxy_cursor = 0  # 代理ip获取游标
        self.proxy_list = []
        self.proxies_scheduler_start()

    def proxies_scheduler_start(self):
        scheduler = BackgroundScheduler()
        scheduler.add_job(self._proxies_refresh, "interval", seconds=30, next_run_time=datetime.datetime.now())
        scheduler.start()
        time.sleep(1)  # 等待_proxies_refresh执行

    def _proxies_refresh(self):
        """ 一次获取适量代理ip """
        self.proxy_cursor, ips = redis_cli.hscan('useful_proxy', cursor=self.proxy_cursor, count=50)
        if ips:
            self.proxy_list.clear()
            for ip in dict(ips).keys():
                self.proxy_list.append({'http': ip})

    @staticmethod
    def wait_proxies():
        """ 等待获取足够的代理ip """
        for i in range(300):
            proxy_num = redis_cli.hlen('useful_proxy')
            if proxy_num > 4:
                return True
            print('\rwait for enough proxies(%d)... %ds' % (proxy_num, i), end='')
            time.sleep(1)
        logging.error("Not have enough proxies!Please check proxy module and run process again.")
        return False

    @property
    def all_proxies(self):
        return self.proxy_list

    @property
    def one_random(self):
        return random.choice(self.proxy_list)
