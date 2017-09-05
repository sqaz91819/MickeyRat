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


def go_go_id(start: int, end: int)-> None:
    with mongodb.Mongodb() as db:

        jie_ba_db_data = db.num_articles("jie_ba_Articles", start, end-start+1)

        if len(jie_ba_db_data) < end-start:
            i = start + len(jie_ba_db_data)
        else:
            i = end+1

        x = 1
        for a in jie_ba_db_data:
            if "id" not in a:
                articles_list = db.search_title("articles", a["title"][a["title"].find("]")+1:])
                w_num = 0
                count = 0
                temp = list(range(0, len(articles_list)))
                temp2 = []
                while len(temp) > 1:
                    if len(a["segments"]) < w_num:
                        break
                    w2 = a["segments"][w_num]
                    for ind in temp:
                        if articles_list[int(ind)]["content"].find(w2) == count:
                            temp2.append(int(ind))
                    if temp2:
                        temp = temp2
                        temp2 = []
                    count += len(a["segments"][w_num])
                    w_num += 1
                db.update_one_id("jie_ba_Articles", a["_id"], articles_list[int(temp[0])]["_id"])
            log(getframeinfo(currentframe()), x, "/", i, " finished!")
            x += 1


def go_go_encode(start: int, end: int)-> None:

    with mongodb.Mongodb() as db:

        jie_ba_db_data = db.num_articles("jie_ba_Articles", start, end-start+1)
        tf_idf = db.search_any("record", "the標題", "tf_idf_dict")
        if tf_idf:
            tf_idf_dict = tf_idf[0]
        else:
            tf_idf_dict = {"the標題": "tf_idf_dict"}

        if len(jie_ba_db_data) < end-start:
            a = start + len(jie_ba_db_data)
        else:
            a = end+1

        x = 1
        for i in jie_ba_db_data:
            if "encode" not in i:
                encode = []
                for word in i["segments"]:
                    if word not in tf_idf_dict:
                        tf_idf_dict[word] = len(tf_idf_dict)
                        log(getframeinfo(currentframe()), "tf_idf_dict insert ", word)
                        db.db["record"].remove({"the標題": "tf_idf_dict"})
                        db.insert_one("record", tf_idf_dict)
                    encode.append(tf_idf_dict[word])
                db.update_one_encode("jie_ba_Articles", i["_id"], encode)
            log(getframeinfo(currentframe()), x, "/", a, " finished!")
            x += 1


def interface(search_key: str)->list:
    raw_articles_list = []
    jie_ba_articles_list = []
    with mongodb.Mongodb() as db:
        log(getframeinfo(currentframe()), 'searching title in "articles":', search_key)
        raw_articles_list = db.search_title("articles", search_key)
        log(getframeinfo(currentframe()), 'searching title in "articles":', search_key, 'finished')

        log(getframeinfo(currentframe()), 'searching title in "jie_ba_Articles":', search_key)
        jie_ba_articles_list = db.search_title("jie_ba_Articles", search_key)
        log(getframeinfo(currentframe()), 'searching title in "jie_ba_Articles":', search_key, 'finished')

    result_list = []
    current_progress = 1
    total = len(jie_ba_articles_list)
    assert len(raw_articles_list) == total, \
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
