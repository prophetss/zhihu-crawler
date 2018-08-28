from bs4 import BeautifulSoup
from functools import wraps
import requests
import redis
import time

# redis连接
pool = redis.ConnectionPool(host='localhost', port=6379, db=0)

r = redis.Redis(connection_pool=pool)

'''
抓取速度控制，请求一次停顿时间单位秒，如果代理ip没有或者过少会被知乎服务器检测出异常
目前自测调用get_proxies_list可设为0，调用get_proxies_list1至少设置为0.5
'''
sleep_time = 0

# 通用请求头
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 \
 18  16 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}


def get_proxies_list1():
    '从https://www.kuaidaili.com/free/inha/抓取免费代理ip,只抓一页15个'
    bf = BeautifulSoup(requests.get('https://www.kuaidaili.com/free/').text, 'html.parser')
    ip_list = []
    for e in bf.tbody.find_all('tr'):
        m = e.get_text().split('\n')
        ip_list.append({m[4]: m[1] + ':' + m[2]})
    return ip_list


def get_proxies_list():
    '需运行https://github.com/jhao104/proxy_pool此程序'
    ups = []
    for ip in r.hkeys('useful_proxy'):
        ups.append({'http': ip})
    return ups


def running_time(func):
    '函数运行时间包装器'

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print('%s Running Time:%.2f' % (func.__name__, end - start))
        return result

    return wrapper


def error_print(e, count=[0]):
    '异常打印,最多接收10000次异常，防止网络或其他问题导致日志大小无限扩增'
    with open('crawl_error.log', mode='a+') as f:
        f.writelines('time:%s.%s\n' % (time.asctime(), str(e)))
    count[0] = count[0] + 1
    if count[0] > 10000:
        raise 'Errors exceeds maximum!'
