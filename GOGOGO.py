# coding=utf-8
from nlp import get_JIEBA
from crawler_api import mongodb


def go_go_go(num: int)-> None:

    with mongodb.Mongodb() as db:

        db.db["record"].remove({"the標題": "tf_idf_dict"})

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

    get_JIEBA.up_dict()


def interface(search_key: str)->list:

    with mongodb.Mongodb() as db:
        '''
        original_db_data = db.db_all("articles")
        jie_ba_db_data = db.db_all("jie_ba_Articles")

        if len(jie_ba_db_data) < len(original_db_data):
            print('original articles has {0} , jie ba articles has {1}'.format(len(original_db_data),
                                                                               len(jie_ba_db_data)))
            an = input('press number 0 to update or any key to skip')

            if an == 0:
                for i in range(len(jie_ba_db_data), len(original_db_data)):
                    jie_ba_return = get_JIEBA.get_jie_ba(original_db_data[i]["content"])
                    jie_ba_return["title"] = original_db_data[i]["title"]
                    db.insert_one("jie_ba_Articles", jie_ba_return)
                    print("{0}/{1} finished!".format(i, len(original_db_data)))
        '''
        tf_idf_dict = get_JIEBA.get_tf_idf()

        articles_list = db.search_title("articles", search_key)
        jie_ba_articles_list = db.search_title("jie_ba_Articles", search_key)

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
            a["url"] = articles_list[int(temp[0])]["url"]
            a["date_added"] = articles_list[int(temp[0])]["date_added"]
            a["content"] = articles_list[int(temp[0])]["content"]

        x = 1
        for article in jie_ba_articles_list:
            encode = []
            for word in article["segments"]:
                encode.append(tf_idf_dict[word])
            article["encoded"] = encode
            print("{0}/{1} encoded".format(x, len(jie_ba_articles_list)))
            x += 1

        return jie_ba_articles_list


'''
with mongodb.Mongodb() as db:
    db.create_col("jie_ba_Articles")
    db.create_col("record")
'''

# interface("模仿遊戲")

# go_go_go(5)
