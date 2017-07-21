from time import time
from os import path
from pymongo import MongoClient
# from pymongo import collection
from crawler_api import crawler


def read_path(filename):
    with open(filename, 'r') as file:
        path = file.read()
    return path


def init():
    server_path = read_path(path.join('crawler_api', 'server_path.txt'))
    client = MongoClient(server_path, 80)
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
# collection.Collection(init(), "articles", create=True)
# test = crawler.json_read("15590.txt")
# inset_many(test)
db_search("你的名字")
