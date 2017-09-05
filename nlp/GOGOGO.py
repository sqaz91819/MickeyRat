# coding=utf-8
from nlp import get_JIEBA
from crawler_api import mongodb
from inspect import currentframe, getframeinfo
from Logger import log


def go_go_go(num: int)-> None:

    with mongodb.Mongodb() as db:

        original_db_data = db.db_all("articles")
        jie_ba_db_data = db.db_all("jie_ba_Articles")

        if len(jie_ba_db_data)+num < len(original_db_data):
            a = len(jie_ba_db_data)+num-1
        else:
            a = len(original_db_data)

        for i in range(len(jie_ba_db_data), (len(jie_ba_db_data)+num)):
            if i < len(original_db_data):
                jie_ba_return = get_JIEBA.get_jie_ba(original_db_data[i]["content"])
                jie_ba_return["title"] = original_db_data[i]["title"]
                db.insert_one("jie_ba_Articles", jie_ba_return)
                print("{0}/{1} finished!".format(i, a))


def interface(search_key: str)->list:

    with mongodb.Mongodb() as db:

        log(getframeinfo(currentframe()), 'searching title in "articles":', search_key)
        articles_list = db.search_title("articles", search_key)
        log(getframeinfo(currentframe()), 'searching title in "articles":', search_key, 'finished')

        log(getframeinfo(currentframe()), 'searching title in "jie_ba_Articles":', search_key)
        jie_ba_articles_list = db.search_title("jie_ba_Articles", search_key)
        log(getframeinfo(currentframe()), 'searching title in "jie_ba_Articles":', search_key, 'finished')

        x = 1
        log(getframeinfo(currentframe()), 'jie_ba_articles_list processing started')
        for a in jie_ba_articles_list:
            w_num = 0
            count = 99
            temp = list(range(0, len(articles_list)))
            while len(temp) > 1:
                w2 = a["segments"][w_num]
                for ind in temp:
                    if articles_list[int(ind)]["content"].find(w2) == -1:
                        del temp[temp.index(ind)]
                    elif articles_list[int(ind)]["content"].find(w2) > count:
                        del temp[temp.index(ind)]
                    elif articles_list[int(ind)]["content"].find(w2) < count:
                        count = articles_list[int(ind)]["content"].find(w2)
                        temp = temp[temp.index(ind):]
                w_num += 1
                count = 99

            a["author"] = articles_list[int(temp[0])]["author"]
            a["label"] = articles_list[int(temp[0])]["label"]
            a["score"] = articles_list[int(temp[0])]["score"]
            a["url"] = articles_list[int(temp[0])]["url"]
            a["date_added"] = articles_list[int(temp[0])]["date_added"]
            a["content"] = articles_list[int(temp[0])]["content"]

            log(getframeinfo(currentframe()), 'fetching get_tf_idf')
            tf_idf_dict = get_JIEBA.get_tf_idf(a["segments"])
            log(getframeinfo(currentframe()), 'fetching get_tf_idf finished')

            log(getframeinfo(currentframe()), 'tf_idf_dict synthesising started')
            encode = []
            for word in a["segments"]:
                encode.append(tf_idf_dict[word])
            a["encoded"] = encode
            log(getframeinfo(currentframe()), 'tf_idf_dict synthesising finished')

            log(getframeinfo(currentframe()), 'articles ', x, '/', len(jie_ba_articles_list), ' encoded')
            x += 1
        log(getframeinfo(currentframe()), 'jie_ba_articles_list processing finished')

        return jie_ba_articles_list


def get_all_data()->list:
    raw_articles_list = []
    jie_ba_articles_list = []
    with mongodb.Mongodb() as db:
        log(getframeinfo(currentframe()), 'get all data in "articles"')
        raw_articles_list = db.db_all("articles")
        log(getframeinfo(currentframe()), 'get all data in "articles" finished')

        log(getframeinfo(currentframe()), 'get all data in "jie_ba_Articles"')
        jie_ba_articles_list = db.db_all("jie_ba_Articles")
        log(getframeinfo(currentframe()), 'get all data in "jie_ba_Articles" finished')

    result_list = []
    current_progress = 1
    total = len(jie_ba_articles_list)
    assert len(raw_articles_list) == total,\
        'collection "articles"{} and collection "jie_ba_Articles"{} mismatch!'.format(len(raw_articles_list), total)

    log(getframeinfo(currentframe()), 'synthesising result list started')
    for jieba_article, raw_article in zip(jie_ba_articles_list, raw_articles_list):
        result_dict = {**jieba_article, **raw_article}
        '''
        jieba_article["author"] = raw_article["author"]
        jieba_article["label"] = raw_article["label"]
        jieba_article["score"] = raw_article["score"]
        jieba_article["url"] = raw_article["url"]
        jieba_article["date_added"] = raw_article["date_added"]
        jieba_article["content"] = raw_article["content"]
        '''

        log(getframeinfo(currentframe()), 'fetching get_tf_idf')
        tf_idf_dict = get_JIEBA.get_tf_idf(result_dict["segments"])
        log(getframeinfo(currentframe()), 'fetching get_tf_idf finished')

        log(getframeinfo(currentframe()), 'encoding started')
        encode = []
        for word in result_dict["segments"]:
            encode.append(tf_idf_dict[word])
        result_dict["encoded"] = encode
        log(getframeinfo(currentframe()), 'encoding finished')

        result_list.append(result_dict)
        log(getframeinfo(currentframe()), 'articles ', current_progress, '/', total, ' encoded')
        current_progress += 1
    log(getframeinfo(currentframe()), 'synthesising result list finished')

    return result_list


def decode(query: list)->list:

    with mongodb.Mongodb() as db:

        the_dict = db.search_any("record", "the標題", "tf_idf_dict")[0]

        for word, num in the_dict.items():
            for q in list(range(0, len(query))):
                if query[q] == num:
                    query[q] = word

        return query


'''
with mongodb.Mongodb() as db:
    db.create_col("jie_ba_Articles")
    db.create_col("record")
'''

# interface("模仿遊戲")

# go_go_go(5)
