#encoding=utf-8
import jieba
import crawler
import math
import jieba.posseg as pseg

#產生"frequency_dict.txt"
def Frequency_dict_first_process():
    d = {}
    d["THE總共"] = 0
    crawler.json_write("frequency_dict.txt", d)

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

#將"frequency_dict.txt"重新編號，避免數字重複
def Frequency_dict_least_process():
    dict = crawler.json_read("frequency_dict.txt")
    sorted_dict = sorted(dict, key=dict.get)
    i = 1
    for w in sorted_dict:
        dict[w] = i
        i += 1
    crawler.json_write("frequency_dict.txt", dict)


#結疤分詞，string 為一篇文章內容，使用計出現次數
def Get_jieba( string ) :

    jieba.load_userdict("dict.txt") # 一般辭典
    jieba.load_userdict("movie_list.txt") # 電影辭典

    pseg_words = pseg.cut(string)

    frequency_dict = crawler.json_read("frequency_dict.txt")

    for one_word in pseg_words : # 計算出現次數
        if one_word.word in frequency_dict:
            frequency_dict[one_word.word] += 1
        else:
            frequency_dict[one_word.word] = 1

    crawler.json_write("frequency_dict.txt", frequency_dict)


    answer = {
        'word' : [],
        'flag' : []
    }

    for w in pseg_words:
        answer['word'].append(w.word)
        answer['flag'].append(w.flag)


    return answer

#結疤分詞，string 為一篇文章內容，使用TF-IDF
def Get_jieba_use_tfidf( string ) :

    jieba.load_userdict("dict.txt") # 一般辭典
    jieba.load_userdict("movie_list.txt") # 電影辭典

    pseg_words = pseg.cut(string)

    tf_dict = crawler.json_read("tf_dict.txt")
    idf_dict = crawler.json_read("idf_dict.txt")
    temp_dist = {}

    for one_word in pseg_words : # 計算出現次數 與 總辭數
        if one_word.word in tf_dict:
            tf_dict[one_word.word] += 1
        else :
            tf_dict[one_word.word] = 1
        if one_word.word in temp_dist:
            temp_dist[one_word.word] = 1
        else:
            temp_dist[one_word.word] = 1
        tf_dict["THE總共"] += 1

    for word in temp_dist:
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



'''''
t = "昨天很榮幸能去看聲之形 所以一定要來發一下心得 先說結論 我覺得聲之形是部不輸給你的名字的電影"
print(Get_jieba(t))
t = "《牆之魘》的背景設定在臺灣光復初期的白色恐怖時代，但是主要探討的不是那個悲慘年代，而是在這種壓抑的時代氛圍下，一個日本共產主義知識"
print(Get_jieba(t))
'''''

