from nlp import get_JIEBA
from crawler_api import crawler
from crawler_api import mongodb
import time

codedict = ''

def GOGOGO( start, end ):
    tStart = time.time()  # 計時開始
    ans = []

    #--------------------------------------------------------------

    db = mongodb.Mongodb()
    crawler.download(start, end)
    articles = crawler.json_read(str(start) + str(end) + ".txt")

    # --------------------------------------------------------------

    get_JIEBA.tf_dict_first_process()
    get_JIEBA.idf_dict_first_process()
    for a in articles:
        jieba_return = get_JIEBA.Get_jieba(a["content"])
        diction = {
            'id':a["_id"],
            'author':a["author"],
            'label':a["label"],
            'title': a["title"],
            'url': a["url"],
            'date_added':a["date_added"],
            'text': a["content"],
            'msegent': jieba_return['word'],
            'pos': jieba_return['flag']
        }
        ans.append(diction)

    tEnd = time.time()  # 計時結束
    print(tEnd - tStart)

    db.inset_many(ans)


def dict_least_process(useTFIDF):
    if useTFIDF :
        get_JIEBA.tfidf_dict_least_process()
        codedict = 'tfidf_dict.txt'
    else :
        get_JIEBA.Frequency_dict_least_process()
        codedict = "frequency_dict.txt"


def GO100():
    start = crawler.read_log() + 1
    end = start+100
    GOGOGO(start, end)

def GO( num = 10 ):
    start = crawler.read_log() + 1
    end = start + num
    GOGOGO(start, end)



#GOGOGO(1,1)
