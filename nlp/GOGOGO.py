# coding=utf-8
from nlp import get_JIEBA
from crawler_api import crawler
from crawler_api import mongodb


def interface(search_key: str) -> list:

    with mongodb.Mongodb() as db:

        original_db_data = db.db_all("Articles")
        jie_ba_db_data = db.db_all("jie_ba_Articles")

        if len(jie_ba_db_data) < len(original_db_data):
            get_JIEBA.tf_dict_first_process()
            get_JIEBA.idf_dict_first_process()
            for i in range(len(jie_ba_db_data), len(original_db_data)):
                jie_ba_return = get_JIEBA.get_jie_ba(original_db_data[i]["content"])
                jie_ba_return["title"] = original_db_data[i]["title"]
                db.insert_one("jie_ba_Articles", jie_ba_return)
                print("URL : {0}/{1} finished!".format(i, len(original_db_data)))
            tf_idf_dict_name = get_JIEBA.tf_idf_dict_least_process()
            tf_idf_dict = crawler.json_read(tf_idf_dict_name)
        else:
            tf_idf_dict = db.search_any("record", "the標題", "tf_idf_dict_to" + str(len(jie_ba_db_data)))

        articles_list = db.search_title("Articles", search_key)
        jie_ba_articles_list = db.search_title("jie_ba_Articles", search_key)

        for a in articles_list:
            for b in jie_ba_articles_list:
                if a["title"] == b["title"]:
                    a["segments"] = b["segments"]
                    a["pos"] = b["pos"]
                    break

        for article in articles_list:
            encode = []
            for word in article["segments"]:
                encode.append(tf_idf_dict[word])
            article["encoded"] = encode
            print(article["title"])

    return articles_list
