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
    def db_redis_host(self):
        return self.cfg.get('DB_REDIS', 'host')

    @LazyProperty
    def db_redis_port(self):
        return self.cfg.get('DB_REDIS', 'port')

    @LazyProperty
    def db_redis_name(self):
        return self.cfg.get('DB_REDIS', 'name')

    @LazyProperty
    def temp_kw_max(self):
        return self.cfg.get('COMMON', 'temp_kw_max')

    @LazyProperty
    def except_log_name(self):
        return self.cfg.get('COMMON', 'except_log_name')

    @LazyProperty
    def run_log_name(self):
        return self.cfg.get('COMMON', 'run_log_name')


conf = Config()
