from zh_crawl import keywords_generator, zhihu_message_crawl, zhihu_topic_crawl
import time

if __name__ == '__main__':
    # 所有抓取的新话题全部会打印出来
    while True:
        start = time.clock()
        # 待搜索关键词获取，存储至zhTemporaryWords内
        keywords_generator.get_key_words()
        # 搜索关键词所有相关的新话题，存储至zhNewTopicName内
        zhihu_topic_crawl.get_hot_topics()
        # 扩展得到的相关新话题，存储至zhNewTopicName内
        zhihu_topic_crawl.expand_topics()
        # 抓取新话题相关内容，话题关注人数和问题数存至zhTopicMessage中，精华问题存至zhTopicQuestions中
        zhihu_message_crawl.crawl_message()
        print('time:%s completed a round of crawler.Running time:%.2fs\n\n' % (time.asctime(), time.clock() - start))
