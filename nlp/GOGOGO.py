import get_JIEBA
import crawler
import time


def GOGOGO( start, end ):
    tStart = time.time()  # 計時開始
    ans = []

    crawler.download(start, end)
    articles = crawler.json_read(str(start) + str(end) + ".txt")

    get_JIEBA.Frequency_dict_first_process()
    for a in articles:
        print(type(a))
        print(a["url"])
        jieba_return = get_JIEBA.Get_jieba(a["content"])
        diction = {
            'title': a["title"],
            'url': a["url"],
            'tag': a["title"][1:4],
            'text': a["content"],
            'msegent': jieba_return['word'],
            'pos': jieba_return['flag']
        }
        ans.append(diction)

    get_JIEBA.Frequency_dict_least_process()
    tEnd = time.time()  # 計時結束
    print(tEnd - tStart)
    return ans

def GOGOGO2( start, end ):
    tStart = time.time()  # 計時開始
    ans = []

    crawler.download(start, end)
    articles = crawler.json_read(str(start) + str(end) + ".txt")

    get_JIEBA.tf_dict_first_process()
    get_JIEBA.idf_dict_first_process()
    for a in articles:
        jieba_return = get_JIEBA.Get_jieba_use_tfidf(a["content"])
        diction = {
            'title': a["title"],
            'url': a["url"],
            'tag': a["title"][1:4],
            'text': a["content"],
            'msegent': jieba_return['word'],
            'pos': jieba_return['flag']
        }
        ans.append(diction)

    get_JIEBA.tfidf_dict_least_process()
    tEnd = time.time()  # 計時結束
    print(tEnd - tStart)
    return ans

GOGOGO2(1,1)