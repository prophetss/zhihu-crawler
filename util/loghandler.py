from logging.handlers import TimedRotatingFileHandler
from util.common import PROJECT_DIR
from util.config import conf
import logging
import os

LOG_PATH = os.path.join(PROJECT_DIR, 'log')

log_directories = ['exception', 'run']


def create_log_directories(directories):
    for log_dir in directories:
        sub_dir = os.path.join(LOG_PATH, log_dir)
        if not os.path.exists(sub_dir):
            os.makedirs(sub_dir)
    directories.clear()


create_log_directories(log_directories)


class LogHandler(logging.Logger):
    """ 日志模块 """

    def __init__(self, name, stream=True, file=True):
        self.name = name
        logging.Logger.__init__(self, self.name)
        if file:
            self.__set_file_handler()
        if stream:
            self.__set_stream_handler()

    def __set_file_handler(self):
        dirs = {logging.WARN: 'exception', conf.file_log_level: 'run'}
        for k, v in dirs.items():
            file_name = os.path.join(LOG_PATH, v, '{name}.log'.format(name=self.name))
            # 设置日志回滚, 保存在log目录, 一天保存一个文件, 保留30天
            file_handler = TimedRotatingFileHandler(filename=file_name, encoding='utf-8', when='D', interval=1,
                                                    backupCount=30)
            file_handler.suffix = '%Y%m%d.log'
            file_handler.setLevel(k)
            formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
            file_handler.setFormatter(formatter)
            self.addHandler(file_handler)

    def __set_stream_handler(self):
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(conf.stream_log_level)
        self.addHandler(stream_handler)


if __name__ == '__main__':
    log = LogHandler('verify')
    log.error('this is a verify msg')
    log.info('this is a verify msg')
