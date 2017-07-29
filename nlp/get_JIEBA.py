#encoding=utf-8
import jieba
from crawler_api import crawler
import math
import jieba.posseg as pseg

#產生"tf_dict.txt"
def tf_dict_first_process():
    d = {}
    d["THE總共"] = 0
    crawler.json_write("tf_dict.txt", d)

#產生"idf_dict.txt"
def idf_dict_first_process():
    d = {}
    d["THE總共"] = 0
    crawler.json_write("idf_dict.txt", d)

#將"tf_dict.txt"重新編號，避免數字重複
def Frequency_dict_least_process():
    dict = crawler.json_read("tf_dict.txt")
    sorted_dict = sorted(dict, key=dict.get)
    i = 1
    for w in sorted_dict:
        dict[w] = i
        i += 1
    crawler.json_write("frequency_dict.txt", dict)


#結疤分詞，string 為一篇文章內容
def Get_jieba( string ) :

    jieba.load_userdict("dict.txt") # 一般辭典
    jieba.load_userdict("movie_list.txt") # 電影辭典

    pseg_words = pseg.cut(string)

    tf_dict = crawler.json_read("tf_dict.txt")
    idf_dict = crawler.json_read("idf_dict.txt")
    temp = []

    for one_word in pseg_words :
        if one_word.word in tf_dict:    # 計算出現次數 與 總辭數
            tf_dict[one_word.word] += 1
        else :
            tf_dict[one_word.word] = 1
        tf_dict["THE總共"] += 1
        if one_word.word not in temp:  # 計算出現文章數
            temp.append(one_word.word)


    for word in temp:
        if word in idf_dict:
            idf_dict[word] += 1
        else:
            idf_dict[word] = 1

    idf_dict["THE總共"] += 1

    crawler.json_write("tf_dict.txt", tf_dict)
    crawler.json_write("idf_dict.txt", idf_dict)


    answer = {
        'word' : [],
        'flag' : []
    }

    for w in pseg_words:
        answer['word'].append(w.word)
        answer['flag'].append(w.flag)


    return answer




def tfidf_dict_least_process():
    tf_dict = crawler.json_read("tf_dict.txt")
    idf_dict = crawler.json_read("idf_dict.txt")

    for i in tf_dict:
        if i != "THE總共" :
            tf_dict[i] = tf_dict[i] / tf_dict["THE總共"]

    for i in idf_dict:
        if i != "THE總共" :
            idf_dict[i] = math.log10(idf_dict["THE總共"] / idf_dict[i])

    tfidf_dict = {}

    for i in tf_dict:
        if i != "THE總共":
            tfidf_dict[i] = tf_dict[i] * idf_dict[i]

    crawler.json_write("tfidf_dict.txt", tfidf_dict)
