from zh_crawler.keywords_generator.keywords_controller import run as kw_run
from zh_crawler.topics_generator.topics_generator import run as tg_run
from zh_crawler.questions_generator.questions_generator import run as qg_run
from zh_crawler.questions_generator.questions_generator import OUTPUT_PATH
from proxyip.main import run as proxy_run
from db.redis_client import redis_cli
from multiprocessing import Process
from util.config import conf
import time
import os


def wait_proxy():
    """ 等待获取足够的代理ip """
    for i in range(300):
        ip_nums = redis_cli.hlen('useful_proxy')
        if ip_nums > 10:
            return
        print('\rwait for enough proxy ips...', end='')
        time.sleep(1)
    raise RuntimeError("Not have enough proxies!Please check proxyip module and run process again.")


def main():
    """ 主进程 """
    # 代理ip获取，创建2个进程
    proxy_run()
    # 等待代理ip获取，首次运行可能需要等待一段时间
    wait_proxy()

    p_list = list()
    if conf.option != 2:
        # 获取关键词
        p1 = Process(target=kw_run, name='kw_run')
        p_list.append(p1)
        # 获取话题
        p2 = Process(target=tg_run, name='tg_run')
        p_list.append(p2)
    if conf.option != 1:
        # 获取话题对应问题，注意：目前其结果以json格式存放至固定output目录下
        p3 = Process(target=qg_run, name='qg_run')
        p_list.append(p3)

    for p in p_list:
        p.start()
    """
    状态监控，显示抓取到数量，
    validProxyIP: 可用有效代理ip
    zhTemporaryWords：新待搜索关键词
    zhTopicMessage：总话题结果信息（问题数、关注人数等）
    zhNewTopicID：搜索后获取到的新话题id
    zhTopicQuestions：话题精华/讨论问题和文章等相关详细内容
    """
    while True:
        print(
            '\rvalidProxyIP:%d    zhTemporaryWords:%d    zhTopicMessage:%d     zhNewTopicID:%d   zhTopicQuestions:%d' % (
                redis_cli.hlen('useful_proxy'), redis_cli.scard('zhTemporaryWords'), redis_cli.hlen('zhTopicMessage'),
                redis_cli.scard('zhNewTopicID'), len([x for x in os.listdir(OUTPUT_PATH)])), end='')
        time.sleep(10)


if __name__ == '__main__':
    main()
