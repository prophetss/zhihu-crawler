from zh_crawler.keywords_generator.keywords_controller import run as kw_run
from zh_crawler.topics_generator.topics_generator import run as tg_run
from zh_crawler.questions_generator.questions_generator import run as qg_run
from zh_crawler.questions_generator.questions_generator import OUTPUT_PATH
from proxyip.Schedule.ProxyValidSchedule import run as ValidRun
from proxyip.Schedule.ProxyRefreshSchedule import run as RefreshRun
from db.redis_client import redis_cli
from multiprocessing import Process
from util.config import conf
import logging
import time
import os


def kill_all(p_list):
    for p in p_list:
        if p.is_alive():
            p.kill()


def process_monitored(p_list):
    for p in p_list:
        if not p.is_alive():
            return False
    return True


def wait_proxy():
    """ 等待获取足够的代理ip """
    for i in range(300):
        proxyies = redis_cli.hlen('useful_proxy')
        if proxyies > 5:
            return True
        print('\rwait for enough proxies... %ds' % i, end='')
        time.sleep(1)
    logging.error("Not have enough proxies!Please check proxyip module and run process again.")
    return False


def main():
    """ 主进程 """
    # 代理ip获取
    p_list = list()
    p_list.append(Process(target=ValidRun, name='ValidRun'))
    p_list.append(Process(target=RefreshRun, name='RefreshRun'))
    for p in p_list:
        p.start()
    # 等待代理ip获取，首次运行可能需要等待一段时间
    if not wait_proxy():
        kill_all(p_list)
        return
    if conf.option != 2:
        # 获取关键词
        p_list.append(Process(target=kw_run, name='kw_run'))
        # 获取话题
        p_list.append(Process(target=tg_run, name='tg_run'))
    if conf.option != 1:
        # 获取话题对应问题，目前其结果以json格式存放至固定output目录下
        p_list.append(Process(target=qg_run, name='qg_run'))
    for p in p_list:
        if not p.is_alive():
            p.start()
    """
    状态监控，显示抓取到数量，
    validProxyIP: 可用有效代理ip
    zhTemporaryWords：新待搜索关键词
    zhTopicMessage：总话题结果信息（问题数、关注人数等）
    zhNewTopicID：搜索后获取到的新话题id
    zhTopicQuestions：话题精华/讨论问题和文章等相关详细内容
    """
    while process_monitored(p_list):
        print(
            '\rvalidProxyIP:%d    zhTemporaryWords:%d    zhTopicMessage:%d     zhNewTopicID:%d   zhTopicQuestions:%d' % (
                redis_cli.hlen('useful_proxy'), redis_cli.scard('zhTemporaryWords'), redis_cli.hlen('zhTopicMessage'),
                redis_cli.scard('zhNewTopicID'), len(os.listdir(OUTPUT_PATH))), end='')
        time.sleep(10)
    kill_all(p_list)  # 退出所有进程


if __name__ == '__main__':
    main()
