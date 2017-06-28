from time import time
from pymongo import MongoClient
# from pymongo import collection


def init():
    client = MongoClient('localhost', 27017)
    db = client.test
    return db


def insert_one(doc):
    db = init()
    result = db.articles.insert_one(doc)
    print(result.inserted_id)


def inset_many(docs):
    db = init()
    result = db.articles.insert_many([doc for doc in docs if doc is not None])
    print(result.inserted_ids)


def db_search(query):
    start = time()
    db = init()
    docs = db.articles.find({'title': {'$regex': ".*" + query + ".*"}})
    print("Query : " + query + " total : " + str(docs.count()))
    print(str(time() - start) + "secs")
    return docs
# create database
# collection.Collection(database, "namestring", create=True)
# test = json_read("15590.txt")
# inset_many(test)
# db_search("聲之形")
