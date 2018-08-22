from bs4 import BeautifulSoup
import requests
import common
import time

'''
关键词生成模块，用于知乎话题搜索,目前的关键词源有两个，百度热点和百度知道
获取到的关键词会存入zhTemporaryWords表内
'''

try:
    # 知道请求头，这里Cookie的BAIDUID是必须的，否则抓取不到数据
    ZhiDao_Headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 16 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        'Cookie': 'BAIDUID=%s' % requests.get('https://zhidao.baidu.com/browse/', timeout=3).cookies['BAIDUID']}
    # 设置获取的关键词生存期为一天
    common.r.expire('zhKeyWords', 86400)
except Exception as eb:
    common.error_print(eb)


def save_keyword(kw):
    if common.r.sadd('zhKeyWords', kw):
        # 添加未发生覆盖，将此关键词存至zhTemporaryWords内待被搜索
        common.r.sadd('zhTemporaryWords', kw)


# 百度热点内容抓取
def crawl_hot_words():
    # 实时热点 今日热点 七日热点 民生热点 娱乐热点 体育热点
    hot_topic_urls = ('http://top.baidu.com/buzz?b=1&c=513&fr=topcategory_c513',
                      'http://top.baidu.com/buzz?b=341&c=513&fr=topbuzz_b1_c513',
                      'http://top.baidu.com/buzz?b=42&c=513&fr=topbuzz_b1_c513',
                      'http://top.baidu.com/buzz?b=342&c=513&fr=topbuzz_b42_c513',
                      'http://top.baidu.com/buzz?b=344&c=513&fr=topbuzz_b342_c513',
                      'http://top.baidu.com/buzz?b=344&c=513&fr=topbuzz_b342_c513')
    for url in hot_topic_urls:
        try:
            req = requests.get(url=url)
            req.encoding = req.apparent_encoding
            bf = BeautifulSoup(req.text, "html.parser")
            for tp in map(lambda x: x.string, bf.find_all('a', class_="list-title")):
                save_keyword(tp)
        except Exception as e:
            common.error_print('get hot topic failed! url=%s %s' % (url, e))
        else:
            print('get hot topic success! url=%s' % url)


# 获取知道问题内容的关键词
def zd_question_keywords(url):
    try:
        req = requests.get(url, timeout=3)
        req.encoding = req.apparent_encoding
        return map(lambda x: x.string, BeautifulSoup(req.text, "html.parser").find_all('li', class_='word grid'))
    except Exception as e:
        common.error_print('get zhidao question keywords failed! %s', e)


# 百度知道关键词抓取，关键词有两部分，1.问题内容包含的关键词，2.问题所属的关键词
def crawl_zhidao_words():
    try:
        req = requests.get(url='https://zhidao.baidu.com/list?_pjax=%23j-question-list-pjax-container',
                           headers=ZhiDao_Headers, timeout=3)
        req.encoding = req.apparent_encoding
        bf = BeautifulSoup(req.text, "html.parser")
        for qs in bf.find_all('div', class_='question-title-section'):
            # 问题所属领域关键词提取
            for qt in map(lambda x: x.string.replace('\n', ''), qs.find_all('a', class_='tag-item')):
                save_keyword(qt)
            # 问题内容包含关键词提取
            for qm in zd_question_keywords(qs.a.get('href')):
                save_keyword(qm)
    except Exception as ek:
        common.error_print('get zhidao keywords failed! %s' % ek)
    else:
        print('get zhidao keywords success!')


# 获取新待搜索关键词，结果存入zhTemporaryWords表中
def get_key_words():
    start = time.clock()
    # 清空临时关键字
    common.r.delete('zhTemporaryWords')
    # 这里每个方法获取关键词都是独立的，也可以自己添加其他的，最后存储至zhTemporaryWords表内即可
    # crawl_hot_words()
    crawl_zhidao_words()
    print('Running keywords_generator time: %.2f Seconds\n' % (time.clock() - start))
