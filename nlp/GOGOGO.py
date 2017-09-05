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
                jie_ba_return["id"] = original_db_data[i]["_id"]
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
            count = 0
            temp = list(range(0, len(articles_list)))
            temp2 = []
            while len(temp) > 1:
                w2 = a["segments"][w_num]
                for ind in temp:
                    if articles_list[int(ind)]["content"].find(w2) == count:
                        temp2.append(int(ind))
                if temp2:
                    temp = temp2
                    temp2 = []
                count += len(a["segments"][w_num])
                w_num += 1

            a["author"] = articles_list[int(temp[0])]["author"]
            a["label"] = articles_list[int(temp[0])]["label"]
            a["score"] = articles_list[int(temp[0])]["score"]
            a["url"] = articles_list[int(temp[0])]["url"]
            a["date_added"] = articles_list[int(temp[0])]["date_added"]
            a["content"] = articles_list[int(temp[0])]["content"]
            a["id"] = articles_list[int(temp[0])]["_id"]

            log(getframeinfo(currentframe()), 'update id')
            db.update_one_id("jie_ba_Articles", a["_id"], articles_list[int(temp[0])]["_id"])
            log(getframeinfo(currentframe()), 'update id finished')

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

    with mongodb.Mongodb() as db:

        log(getframeinfo(currentframe()), 'get all data in "articles"')
        articles_list = db.db_all("articles")
        log(getframeinfo(currentframe()), 'get all data in "articles" finished')

        log(getframeinfo(currentframe()), 'get all data in "jie_ba_Articles"')
        jie_ba_articles_list = db.db_all("jie_ba_Articles")
        log(getframeinfo(currentframe()), 'get all data in "jie_ba_Articles" finished')

        x = 1
        log(getframeinfo(currentframe()), 'jie_ba_articles_list processing started')
        for a in jie_ba_articles_list:
            w_num = 0
            count = 0
            temp = list(range(0, len(articles_list)))
            temp2 = []
            while len(temp) > 1:
                w2 = a["segments"][w_num]
                for ind in temp:
                    if articles_list[int(ind)]["content"].find(w2) == count:
                        temp2.append(int(ind))
                if temp2:
                    temp = temp2
                    temp2 = []
                count += len(a["segments"][w_num])
                w_num += 1

            a["author"] = articles_list[int(temp[0])]["author"]
            a["label"] = articles_list[int(temp[0])]["label"]
            a["score"] = articles_list[int(temp[0])]["score"]
            a["url"] = articles_list[int(temp[0])]["url"]
            a["date_added"] = articles_list[int(temp[0])]["date_added"]
            a["content"] = articles_list[int(temp[0])]["content"]
            a["id"] = articles_list[int(temp[0])]["_id"]

            log(getframeinfo(currentframe()), 'update id')
            db.update_one_id("jie_ba_Articles", a["_id"], articles_list[int(temp[0])]["_id"])
            log(getframeinfo(currentframe()), 'update id finished')

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
