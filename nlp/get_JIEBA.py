# encoding=utf-8
from crawler_api import mongodb
import jieba
import jieba.posseg as pseg
from os import path
from inspect import currentframe, getframeinfo
from Logger import log


# 計算tf_idf
def get_tf_idf(str_list: list)->dict:
    frameinfo = getframeinfo(currentframe())

    with mongodb.Mongodb() as db:

        log(getframeinfo(currentframe()), 'db.search_any("record", "the標題", "tf_idf_dict") started')
        tf_idf = db.search_any("record", "the標題", "tf_idf_dict")
        if tf_idf:
            log(getframeinfo(currentframe()), 'db.search_any("record", "the標題", "tf_idf_dict") finished')
            tf_idf_dict = tf_idf[0]
        else:
            log(getframeinfo(currentframe()), 'db.search_any("record", "the標題", "tf_idf_dict") failed')
            tf_idf_dict = {"the標題": "tf_idf_dict"}

        log(getframeinfo(currentframe()), 'tf_idf_dict add new word started')
        x = len(tf_idf_dict)
        for word in str_list:
            if '.' in word:
                changed_word = word.replace('.', '*')
            else:
                changed_word = word
            if changed_word not in tf_idf_dict:
                tf_idf_dict[changed_word] = x
                x += 1
        log(getframeinfo(currentframe()), 'tf_idf_dict add new word finished')

        log(getframeinfo(currentframe()), 'cleaning db record started')
        db.db["record"].remove({"the標題": "tf_idf_dict"})
        log(getframeinfo(currentframe()), 'cleaning db record finished')

        log(getframeinfo(currentframe()), 'insert tf_idf_dict to db started')
        db.insert_one("record", tf_idf_dict)
        log(getframeinfo(currentframe()), 'insert tf_idf_dict to db finished')

        return tf_idf_dict


# 結疤分詞，string 為一篇文章內容
def get_jie_ba(string: str)->dict:

    jieba.load_userdict(path.join('nlp', 'dict.txt'))        # 一般辭典
    jieba.load_userdict(path.join('nlp', 'movie_list.txt'))  # 電影辭典

    pseg_words = pseg.cut(string)

    word = []
    flag = []

    for one_word in pseg_words:
        if '.' in one_word.word:
            changed_word = one_word.word.replace('.', '*')
        else:
            changed_word = one_word.word
        word.append(changed_word)
        flag.append(one_word.flag)

    ans = {"segments": word, "pos": flag}

    return ans
