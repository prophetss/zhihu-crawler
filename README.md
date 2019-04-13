# 知乎内容爬取（不断完善中...）

知乎数据抓取，通过抓取百度知道关键词来在知乎上搜索相似话题，而后进一步扩展此话题，进而获取全部数据。

内部自动获取代理ip，[原程序](https://github.com/jhao104/proxy_pool)是在网上找的，我对其进行了缩减合并。

抓取一共分为四个部分，待搜索关键词抓取，话题抓取，问题抓取，回答抓取：

待搜索关键词为百度知道实时提问关键词和百度热点实时关键词

话题为redis存储，最终产生2个hash表来存放话题相关结果
1.zhTopicMessage哈希表内存放话题相关信息，key-话题id，value-{'name':名称, 'introduction': 简介, 'questions':问题数,'top_answers':精华问题数, 'followers':关注人数, 'best_answerers':优秀回答者人数} 
2.zhTopicDAG内存放话题结构，key-父话题id，value-子话题id队列

问题由于过于庞大目前以json格式保存在output目录下，具体可以通过Config.ini内设置开关，格式为下（不同类型可能略有差异）：
key-类型（文章/问题...），value-{key-id, value-{'question/title':问题/文章名称, author':作者,
        'gender':性别,'author_badge':作者标签, 'author_headline':作者签名, 'author_url_token':作者url标识，excerpt':摘录，
        'created_time':创建时间, 'updated_time':最后更新时间, 'comment_count':'评论数', likes':点赞数}}

data文件夹内为我抓取到的zhTopicMessage的输出内容，一共十万六千多个话题信息，下面是一个话题例子展示： 
19667537:{'name': '丹尼斯·罗德曼（Dennis Rodman）', 'introduction': '丹尼斯·罗德曼（Dennis Rodman），1961年5月13日出生于美国新泽西州特伦顿，前美国职业篮球运动员，司职大前锋，绰号“大虫”（The Worm）。丹尼斯·罗德曼在1986年NBA选秀中于第2轮第27顺位被底特律活塞队选中，1995-96赛季被交易至芝加哥公牛队，联手迈克尔·乔丹，斯科特·皮蓬组成“铁三角”组合，并于当赛季常规赛收获72胜10负的历史第2好战绩。在1995-96赛季开始到1997-98赛季，连续三年获得NBA总冠军，建立公牛王朝。在1999-00赛季为小牛效力12场比赛后于2000年3月8日宣布从NBA退役。退役之后的罗德曼曾参加国外联赛，并于2006年正式宣布退役。在20年的职业生涯中，罗德曼共5次夺得NBA总冠军，2次入选NBA全明星阵容，2次入选NBA最佳阵容三阵，2次当选NBA年度最佳防守球员，7次入选NBA最佳防守阵容一阵，1994年入选NBA最佳防守阵容二阵，1992-98年间，连续七年获得NBA篮板王的称号，生涯共抢下11954个篮板，位列NBA历史篮板榜第22位，被誉为最会抢篮板的大前锋。2011年4月2日，丹尼斯·罗德曼的10号球衣被活塞队退役。同年8月13日，罗德曼入选奈·史密斯篮球名人纪念堂。', 'questions_count': 33, 'best_answers_count': 23, 'followers_count': 643, 'best_answerers_count': 46}
