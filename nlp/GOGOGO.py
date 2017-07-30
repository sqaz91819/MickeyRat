from nlp import get_JIEBA
import time
from crawler_api import crawler
from crawler_api import mongodb



#收文章
def GOToDownload( start, end ):
    tStart = time.time()  # 計時開始
    ans = []

    #--------------------------------------------------------------

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
            'segments': jieba_return['word'],
            'pos': jieba_return['flag']
        }
        ans.append(diction)

    tEnd = time.time()  # 計時結束
    print(tEnd - tStart)

    with mongodb.Mongodb() as db:
        db.insert_many(ans)


#更新舊有文章，加入分詞結果
def GOToUpdate():
    with mongodb.Mongodb() as db:
        articles = db.db_all()

    get_JIEBA.tf_dict_first_process()
    get_JIEBA.idf_dict_first_process()
    for a in articles:
        jieba_return = get_JIEBA.Get_jieba(a["content"])
        with mongodb.Mongodb() as db:
            db.update_one(a["_id"], jieba_return['word'], jieba_return['flag'])


#產生encode字典
def dict_least_process(useTFIDF = True):
    if useTFIDF :
        codedict = get_JIEBA.tfidf_dict_least_process()
    else :
        codedict = get_JIEBA.Frequency_dict_least_process()
    return codedict


#介面
def InterFace(keyword):
    with mongodb.Mongodb() as db:
        articles = db.db_search(keyword)
    
    n=dict_least_process()
    dict = crawler.json_read(n)

    for article in articles:
        encode=[]
        for word in article["segments"]:
            encode.append(dict[word])
        article["encoded"] = encode

    return article


def GO100():
    start = crawler.read_log() + 1
    end = start+100
    GOToDownload(start, end)

def GO( num = 10 ):
    start = crawler.read_log() + 1
    end = start + num
    GOToDownload(start, end)


def TTTTest(start=1, end=1):
    ans = []

    # --------------------------------------------------------------

    #crawler.download(start, end)
    articles = crawler.json_read(str(start) + str(end) + ".txt")

    # --------------------------------------------------------------

    get_JIEBA.tf_dict_first_process()
    get_JIEBA.idf_dict_first_process()
    for a in articles:
        jieba_return = get_JIEBA.Get_jieba(a["content"])
        diction = {
            'id': a["_id"],
            'author': a["author"],
            'label': a["label"],
            'title': a["title"],
            'url': a["url"],
            'date_added': a["date_added"],
            'text': a["content"],
            'segments': jieba_return['word'],
            'pos': jieba_return['flag']
        }
        ans.append(diction)
        print(a["title"])

    n=dict_least_process()
    dict = crawler.json_read(n)
    for article in ans:
        encode=[]
        for word in article["segments"]:
            encode.append(dict[word])
        article["encoded"] = encode
        print(article["title"])

    crawler.json_write("test.txt", ans)




#TTTTest(1,1)