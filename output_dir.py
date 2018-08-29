import networkx as nx
import common
import os

'''
    呈现保存的数据，以目录表示话题结构，对应其结构创建目录，每个目录内创建一个文本，文本名为话题名称，
    内容为话题具体相关内容.
'''

zhihu_topic_dag = nx.DiGraph()


def topic_dag_init():
    'redis存储的图结构转换为networkx'
    for k in common.r.hkeys('zhTopicDAG'):
        zhihu_topic_dag.add_node(int(k))
        for v in eval(common.r.hget('zhTopicDAG', k)):
            zhihu_topic_dag.add_node(int(v))
            zhihu_topic_dag.add_edge(*(int(k), int(v)))


def write_message(path, tid):
    '写文件保存具体话题相关内容'
    topic_message = eval(common.r.hget('zhTopicMessage', tid).decode('utf-8'))
    # 话题名称后加双下划线防止名称中有点生成各种各样文件..
    with open(os.path.join(path, topic_message['name'] + '__'), 'wt') as f:
        f.write('关注人数：%s 问题数:%s\n' % (topic_message['followers'], topic_message['questions']))
        for q in eval(common.r.hget('zhTopicQuestions', tid).decode('utf-8')):
            f.write('问题：%s 作者：%s 评论数：%s 点赞数：%s 链接：%s\n' %
                    (q['question'], q['author'], q['contents'], q['likes'], q['href']))


def dag_to_dir(path):
    '将话题结构转成目录结构呈现'
    topic_dag_init()
    for tid in common.r.hkeys('zhTopicMessage'):
        total_path = path
        try:
            # 计算全路径
            for n in nx.shortest_path(zhihu_topic_dag, 19776749, int(tid)):
                total_path = os.path.join(total_path, str(n))
            os.makedirs(total_path, exist_ok=True)
            write_message(total_path, tid)
        except Exception as e:
            common.error_print(e)


dag_to_dir('D:\\')
