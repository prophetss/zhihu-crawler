from requests.exceptions import RequestException
from util.decorator import timethis
from bs4 import BeautifulSoup
from util.loghandler import LogHandler
import requests


class ZhiDaoGenerator:
    """ 百度知道关键词抓取，关键词有两部分，1.问题内容包含的关键词，2.问题所属的关键词 """

    def __init__(self):
        self.logger = LogHandler('zhidao_crawl')
        try:
            # 知道请求头，获取Cookie的BAIDUID，否则抓取不到数据
            self.zhidao_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 16 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
                'Cookie': 'BAIDUID=%s' % requests.get('https://zhidao.baidu.com/browse/', timeout=3).cookies['BAIDUID']}
        except Exception as e:
            raise e

    def __zd_question_keywords(self, url):
        """ 获取知道问题内容的关键词 """
        try:
            req = requests.get(url, timeout=3)
            req.encoding = req.apparent_encoding
            kws = []
            for kw_tag in BeautifulSoup(req.text, "html.parser").find_all('li', class_=lambda class_: class_ and (
                    'word grid' in class_)):
                kw = kw_tag.find(class_="word-text")
                if kw is not None:
                    kws.append(kw.string)
            return kws
        except RequestException as re:
            self.logger.warning(re)
            return []
        except Exception as e:
            raise e

    @timethis
    def crawl_zhidao_words(self, save_keyword):
        """ 百度知道抓取 """
        try:
            req = requests.get(url='https://zhidao.baidu.com/list?_pjax=%23j-question-list-pjax-container',
                               headers=self.zhidao_headers, timeout=3)
            req.encoding = req.apparent_encoding
            for qs in BeautifulSoup(req.text, "html.parser").find_all('div', class_='question-title-section'):
                # 问题所属领域关键词提取
                for qt in map(lambda x: x.string.replace('\n', ''), qs.find_all('a', class_='tag-item')):
                    save_keyword(qt)
                # 问题内容包含关键词提取
                for qm in self.__zd_question_keywords(qs.a.get('href')):
                    save_keyword(str(qm))
        except RequestException as re:
            self.logger.warn(re)
        except Exception as e:
            raise e


if __name__ == '__main__':
    ZhiDaoGenerator().crawl_zhidao_words(print)
