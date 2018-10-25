# -*- coding: utf-8 -*-

from functools import wraps
import time

'''1、2参考：https://python3-cookbook.readthedocs.io/'''


class LazyProperty:
    '''延迟调用+结果保存'''

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            value = self.func(instance)
            setattr(instance, self.func.__name__, value)
            return value


def timethis(func):
    '''运行时间打印'''

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        with open('run.log', 'a+') as f:
            print(func.__name__, round(end - start, 2), 's', file=f)
        return result

    return wrapper


def singleton(cls, *args, **kw):
    '''单例模式'''
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton
