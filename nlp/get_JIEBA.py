# encoding=utf-8
from crawler_api import crawler
from crawler_api import mongodb
import jieba
import jieba.posseg as pseg
import math
import os
import operator


# 產生"tf_dict.txt"
def tf_dict_first_process()->None:
    with mongodb.Mongodb() as db:
        d = db.search_any("record", "the標題", "tf_dict")[0]
        if not d:
            c = {"THE總共": 0, "the標題": "tf_dict"}
            crawler.json_write("tf_dict.txt", c)
        else:
            crawler.json_write("tf_dict.txt", d)


# 產生"idf_dict.txt"
def idf_dict_first_process()->None:
    with mongodb.Mongodb() as db:
        d = db.search_any("record", "the標題", "idf_dict")[0]
        if not d:
            c = {"THE總共": 0, "the標題": "idf_dict"}
            crawler.json_write("idf_dict.txt", c)
        else:
            crawler.json_write("idf_dict.txt", d)


# 計算tf_idf
def tf_idf_dict_least_process()->str:
    tf_dict = crawler.json_read(os.path.join('nlp', "tf_dict.txt"))
    idf_dict = crawler.json_read(os.path.join('nlp', "idf_dict.txt"))

    with mongodb.Mongodb() as db:
        jie_ba_articles_len = len(db.db_all("jie_ba_Articles"))
        db.insert_one("record", tf_dict)     # !!!!!!!!!!需更新的function
        db.insert_one("record", idf_dict)    # !!!!!!!!!!

    for i in idf_dict:
        if i != "THE總共" and i != "the標題":
            idf_dict[i] = 1 - (idf_dict[i] / (idf_dict["THE總共"] + 1))
            # idf_dict[i] = math.log10(idf_dict["THE總共"]+1 / idf_dict[i])

    tf_idf_dict = {}

    for i in tf_dict:
        if i != "THE總共" and i != "the標題":
            # tf_idf_dict[i] = math.log10(tf_dict[i] * idf_dict[i])
            tf_idf_dict[i] = math.log10(tf_dict[i]) * idf_dict[i]

    tf_list = sorted(tf_dict.items(), key=operator.itemgetter(1), reverse=True)
    idf_list = sorted(idf_dict.items(), key=operator.itemgetter(1), reverse=False)
    tf_idf_list = sorted(tf_idf_dict.items(), key=operator.itemgetter(1), reverse=True)

    crawler.json_write("tf_list_to" + str(jie_ba_articles_len) + ".txt", tf_list)
    crawler.json_write("idf_list_to" + str(jie_ba_articles_len) + ".txt", idf_list)
    crawler.json_write("tf_idf_list_to" + str(jie_ba_articles_len) + ".txt", tf_idf_list)

    x = 1
    for key, value in tf_idf_list:
        if key != "THE總共":
            tf_idf_dict[key] = x
            x += 1

    crawler.json_write("tf_idf_dict_to" + str(jie_ba_articles_len) + ".txt", tf_idf_dict)

    tf_idf_dict["the標題"] = "tf_idf_dict_to" + str(jie_ba_articles_len)

    with mongodb.Mongodb() as db:
        db.insert_one("record", tf_idf_dict)

    return str("tf_idf_dict_to" + str(jie_ba_articles_len) + ".txt")


# 結疤分詞，string 為一篇文章內容
def get_jie_ba(string: str)->dict:

    jieba.load_userdict("dict.txt")        # 一般辭典
    jieba.load_userdict("movie_list.txt")  # 電影辭典

    pseg_words = pseg.cut(string)

    tf_dict = crawler.json_read("tf_dict.txt")
    idf_dict = crawler.json_read("idf_dict.txt")
    temp = []
    word = []
    flag = []

    for one_word in pseg_words:
        word.append(one_word.word)
        flag.append(one_word.flag)
        if one_word.word in tf_dict:    # 計算出現次數 與 總辭數
            tf_dict[one_word.word] += 1
        else:
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

    ans = {"segments": word, "pos": flag}

    return ans


# Frequency_dict_least_process()
# tf_idf_dict_least_process()
'''
tf_dict_first_process()
idf_dict_first_process()
x= Get_jieba("還有開大卡車送貨，偶而回家的爸爸住在一個小小的公寓裡頭，麥諾利多是個成績平平的平凡小孩，他的媽媽是典型的望子成龍型家長")
print(x)
'''