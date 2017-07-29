from time import time
from os import path
from pymongo import MongoClient
from pymongo import collection


def read_path(filename):
    with open(filename, 'r') as file:
        path = file.read()
    return path


class Mongodb:
    def __init__(self):
        self.server_path = read_path(path.join('C:/Users/z3901/Documents/GitHub/MickeyRat/crawler_api', 'server_path.txt'))
        self.client = MongoClient(self.server_path, 80)
        self.db = self.client.test

    def create_col(self, c_name):
        collection.Collection(self.db, c_name, create=True)

    def insert_one(self, doc):
        result = self.db.articles.insert_one(doc)
        print(result.inserted_id)

    def inset_many(self, docs):
        result = self.db.articles.insert_many([doc for doc in docs if doc is not None])
        print(result.inserted_ids)

    def db_search(self, query):
        start = time()
        docs = self.db.articles.find({'title': {'$regex': ".*" + query + ".*"}})
        print("Query : " + query + " total : " + str(docs.count()))
        print("Spent time : " + str(time() - start)[0:5] + " secs")
        return list(docs)

    def db_all(self):
        start = time()
        docs = self.db.articles.find({})
        print("Total : " + str(docs.count()))
        print("Spent time : " + str(time() - start)[0:5] + " secs")
        return list(docs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
        print("Database connection closed...")
        if exc_type:
            print("Error type : " + str(exc_type))
            print("Error : " + str(exc_val))
        return True
