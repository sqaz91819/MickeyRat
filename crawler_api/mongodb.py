from time import time
from os import path
from typing import List, DefaultDict
from pymongo import MongoClient, collection
from collections import defaultdict


def read_path(filename):
    with open(filename, 'r') as file:
        server_path = file.read()
    return server_path

Article = DefaultDict
Articles = List[Article]


class Mongodb:
    def __init__(self):
        self.server_path = read_path(path.join('crawler_api',
                                               'server_path.txt'))
        self.client = MongoClient(self.server_path, 80)
        self.db = self.client.test

    def create_col(self, c_name: str) -> None:
        collection.Collection(self.db, c_name, create=True)

    def insert_one(self, col_name: str, doc: Article) -> None:
        result = self.db[col_name].insert_one(doc)
        print(result.inserted_id)

    def insert_many(self, col_name: str, docs: Articles) -> None:
        result = self.db[col_name].insert_many([doc for doc in docs if doc is not None])
        print(result.inserted_ids)

    def search_title(self, col_name: str, query: str) -> Articles:
        start = time()
        docs = self.db[col_name].find({'title': {'$regex': ".*" + query + ".*"}})
        if not docs:
            print("Collection does not exist or no doc match.")
            return []
        print("Query : " + query + " total : " + str(docs.count()))
        print("Spent time : " + str(time() - start)[0:5] + " secs")
        return list(docs)

    def search_label(self, col_name: str, query: str ="雷") -> Articles:
        start = time()
        docs = self.db[col_name].find({'label': {'$regex': ".*" + query + ".*"}})
        if not docs:
            print("Collection does not exist or no doc match.")
            return []
        print("Query : " + query + " total : " + str(docs.count()))
        print("Spent time : " + str(time() - start)[0:5] + " secs")
        return list(docs)

    def search_any(self, col_name: str, field: str, query: str) -> Articles:
        start = time()
        docs = self.db[col_name].find({field: {'$regex': ".*" + query + ".*"}})
        if not docs:
            print("Collection does not exist or no doc match.")
            return []
        print("Query : " + query + " in " + field + " total : " + str(docs.count()))
        print("Spent time : " + str(time() - start)[0:5] + " secs")
        return list(docs)

    def db_all(self, col_name: str) -> Articles:
        start = time()
        docs = self.db[col_name].find({})
        if not docs:
            print("Collection does not exist or empty.")
            return []
        print("Total : " + str(docs.count()))
        print("Spent time : " + str(time() - start)[0:5] + " secs")
        return list(docs)

    def update_one(self, col_name: str, _id: str, segments, pos) -> None:
        result = self.db[col_name].update_one({'_id': _id}, {'$set': {'segments': segments, 'pos': pos}})
        print(result.matched_count)

    def delete_one(self, col_name: str, _id: str) -> None:
        result = self.db[col_name].delete_one({'_id': _id})
        print("Deleted " + str(result))

    def close(self) -> None:
        self.client.close()

    def label_view(self):
        labels = defaultdict(int)
        for article in self.search_label("articles"):
            if article['label'] != article['title']:
                labels[article['label']] += 1
        return labels

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
        print("Database connection closed...")
        if exc_type:
            print("Error type : " + str(exc_type))
            print("Error : " + str(exc_val))
        return True
