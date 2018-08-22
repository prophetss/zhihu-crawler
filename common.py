from bs4 import BeautifulSoup
import requests
import time
import redis

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)

r = redis.Redis(connection_pool=pool)

# 通用请求头
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 \
 18  16 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}


# 从https://www.kuaidaili.com/free/inha/抓取免费代理ip,只抓一页15个
def get_proxies_list1():
    bf = BeautifulSoup(requests.get('https://www.kuaidaili.com/free/').text, 'html.parser')
    ip_list = []
    for e in bf.tbody.find_all('tr'):
        m = e.get_text().split('\n')
        ip_list.append({m[4]: m[1] + ':' + m[2]})
    return ip_list


# 需运行https://github.com/jhao104/proxy_pool此程序
def get_proxies_list():
    ups = []
    for ip in r.hkeys('useful_proxy'):
        ups.append({'http': ip})
    return ups


# 异常打印
def error_print(e):
    with open('crawl_error.log', mode='a+') as f:
        f.writelines('time:%s.%s\n' % (time.asctime(), str(e)))


error_print("ddd")
