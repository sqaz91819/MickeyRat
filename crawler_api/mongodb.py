from time import time
from os import path
from typing import List, DefaultDict
from pymongo import MongoClient, collection


def read_path(filename):
    with open(filename, 'r') as file:
        server_path = file.read()
    return server_path

article = DefaultDict
articles = List[article]


class Mongodb:
    def __init__(self):
        self.server_path = read_path(path.join('C:/Users/z3901/Documents/GitHub/MickeyRat/crawler_api',
                                               'server_path.txt'))
        self.client = MongoClient(self.server_path, 80)
        self.db = self.client.test

    def create_col(self, c_name: str) -> None:
        collection.Collection(self.db, c_name, create=True)

    def insert_one(self, doc: article) -> None:
        result = self.db.articles.insert_one(doc)
        print(result.inserted_id)

    def insert_many(self, docs: articles) -> None:
        result = self.db.articles.insert_many([doc for doc in docs if doc is not None])
        print(result.inserted_ids)

    def db_search(self, query: str) -> articles:
        start = time()
        docs = self.db.articles.find({'title': {'$regex': ".*" + query + ".*"}})
        print("Query : " + query + " total : " + str(docs.count()))
        print("Spent time : " + str(time() - start)[0:5] + " secs")
        return list(docs)

    def db_all(self) -> articles:
        start = time()
        docs = self.db.articles.find({})
        print("Total : " + str(docs.count()))
        print("Spent time : " + str(time() - start)[0:5] + " secs")
        return list(docs)

    def update_one(self, _id: str, segments, pos) -> None:
        result = self.db.articles.update_one({'_id': _id}, {'$set': {'segments': segments, 'pos': pos}})
        print(result.matched_count)

    def close(self) -> None:
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
        print("Database connection closed...")
        if exc_type:
            print("Error type : " + str(exc_type))
            print("Error : " + str(exc_val))
        return True
