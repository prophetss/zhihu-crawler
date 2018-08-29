# 知乎内容爬取
非登录模式下通过抓取百度知道关键词来在知乎上搜索相似话题，而后进一步扩展此话题。目前实测一小时抓取3000个左右包括话题相关内容和精华问题等 
存储数据库为redis，最终产生3个hash表来存放结果   
1.zhTopicMessage哈希表内key-话题id，value-字典{'name':名称, 'questions':问题数, 'followers',关注人数}  
2.zhTopicQuestions哈希表key-话题id，value-字典{'question':问题, 'anthor':作者, 'contents':'评论数':likes':点赞数，‘href':链接}  
3.zhTopicDAG内key-父话题id，value-子话题id队列  

output.py是一个单独运行的文件，是将存储的话题结构合内容按目录输出并生成对应文件保存相关内容
