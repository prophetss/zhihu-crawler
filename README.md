# 知乎内容爬取
非登录模式下通过抓取百度知道关键词来在知乎上搜索相似话题，而后进一步扩展此话题。目前实测一天可以抓取一万多个话题 ＜/br＞
存储数据库为redis，最终产生4个hash表来存放结果：＜/br＞
1.zhTopicName，key-话题，value-话题id； ＜/br＞
2.zhTopicDAG（保存话题结构，有向无环图），key-父话题id，value-子话题id列表； ＜/br＞
3.zhTopicMessage，key-话题id，value-关注人数和问题数； ＜/br＞
4.zhTopicQuestions，key-话题id，value-此话题精华问题相关内容  ＜/br＞
