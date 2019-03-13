# -*- coding: utf-8 -*-

from configparser import ConfigParser
from util.decorator import LazyProperty
from util.decorator import singleton
import os


@singleton
class Config(object):
    def __init__(self):
        self.cfg = ConfigParser()
        self.cfg.read(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Config.ini'), encoding='utf-8')

    @LazyProperty
    def option(self):
        return int(self.cfg.get('MAIN', 'option'))

    @LazyProperty
    def essence_nums(self):
        return int(self.cfg.get('MAIN', 'essence'))

    @LazyProperty
    def top_activity_nums(self):
        return int(self.cfg.get('MAIN', 'top_activity'))

    @LazyProperty
    def db_redis_host(self):
        return self.cfg.get('DB_REDIS', 'host')

    @LazyProperty
    def db_redis_port(self):
        return self.cfg.get('DB_REDIS', 'port')

    @LazyProperty
    def db_redis_name(self):
        return self.cfg.get('DB_REDIS', 'name')

    @LazyProperty
    def proxy_getter_functions(self):
        return self.cfg.options('ProxyGetter')

    @LazyProperty
    def temp_kw_max(self):
        return self.cfg.get('COMMON', 'temp_kw_max')

    @LazyProperty
    def stream_log_level(self):
        return int(self.cfg.get('RUN_LOG', 'stream_log_level'))

    @LazyProperty
    def file_log_level(self):
        return int(self.cfg.get('RUN_LOG', 'file_log_level'))


conf = Config()
