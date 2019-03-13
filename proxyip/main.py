# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     main.py  
   Description :  运行主函数
   Author :       JHao
   date：          2017/4/1
-------------------------------------------------
   Change Activity:
                   2017/4/1: 
-------------------------------------------------
"""
__author__ = 'JHao'

import sys
from multiprocessing import Process

sys.path.append('.')
sys.path.append('..')

from proxyip.Schedule.ProxyValidSchedule import run as ValidRun
from proxyip.Schedule.ProxyRefreshSchedule import run as RefreshRun


def run():
    p_list = list()
    p2 = Process(target=ValidRun, name='ValidRun')
    p_list.append(p2)
    p3 = Process(target=RefreshRun, name='RefreshRun')
    p_list.append(p3)
    for p in p_list:
        p.start()


if __name__ == '__main__':
    run()
