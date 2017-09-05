from time import time
from os import path
from typing import List, DefaultDict
from pymongo import MongoClient, collection
from collections import defaultdict
from inspect import currentframe, getframeinfo
from Logger import log
from traceback import format_tb


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
        log(getframeinfo(currentframe()), 'DB insert result : ', result.inserted_id)

    def insert_many(self, col_name: str, docs: Articles) -> None:
        result = self.db[col_name].insert_many([doc for doc in docs if doc is not None])
        log(getframeinfo(currentframe()), 'DB insert result : ', result.inserted_ids)

    def search_title(self, col_name: str, query: str) -> Articles:
        start = time()
        docs = self.db[col_name].find({'title': {'$regex': ".*" + query + ".*"}})
        if not docs:
            log(getframeinfo(currentframe()), 'Collection does not exist or no doc match.')
            return []
        lst = list(docs)
        log(getframeinfo(currentframe()), 'Query : ', query, ' total : ', str(len(lst)))
        log(getframeinfo(currentframe()), 'Spent time : ', str(time() - start)[0:5], ' secs')
        return lst

    def search_label(self, col_name: str, query: str ="雷") -> Articles:
        start = time()
        docs = self.db[col_name].find({'label': {'$regex': ".*" + query + ".*"}})
        if not docs:
            log(getframeinfo(currentframe()), 'Collection does not exist or no doc match.')
            return []
        lst = list(docs)
        log(getframeinfo(currentframe()), 'Query : ', query, ' total : ', str(len(lst)))
        log(getframeinfo(currentframe()), 'Spent time : ', str(time() - start)[0:5], ' secs')
        return lst

    def search_any(self, col_name: str, field: str, query: str) -> Articles:
        start = time()
        docs = self.db[col_name].find({field: {'$regex': ".*" + query + ".*"}})
        if not docs:
            log(getframeinfo(currentframe()), 'Collection does not exist or no doc match.')
            return []
        lst = list(docs)
        log(getframeinfo(currentframe()), 'Query : ', query, ' in ', field, ' total : ', str(len(lst)))
        log(getframeinfo(currentframe()), 'Spent time : ', str(time() - start)[0:5], ' secs')
        return lst

    def db_all(self, col_name: str) -> Articles:
        start = time()
        docs = self.db[col_name].find({})
        if not docs:
            log(getframeinfo(currentframe()), 'Collection does not exist or empty.')
            return []
        lst = list(docs)
        log(getframeinfo(currentframe()), 'Total : ', str(len(lst)))
        log(getframeinfo(currentframe()), 'Spent time : ', str(time() - start)[0:5], ' secs')
        return lst

    def update_one_id(self, col_name: str, _id: str, new_id: str) -> None:
        result = self.db[col_name].update_one({'_id': _id}, {'$set': {'id': new_id}})
        print(result.matched_count)

    def update_score(self, col_name: str, _id: str, score: int) -> None:
        self.db[col_name].update_one({'_id': _id}, {'$set': {'score': score}})

    def update_all_score(self, col_name: str, labels) -> None:
        docs = self.db_all(col_name)

        for index, doc in enumerate(docs):
            self.update_score(col_name, doc['_id'], labels[doc['label']] if doc['label'] in labels else -1)
            if index % 1000 == 0:
                log(getframeinfo(currentframe()), '1000 articles updated.')

        log(getframeinfo(currentframe()), 'All articles updated!')

    def delete_one(self, col_name: str, _id: str) -> None:
        result = self.db[col_name].delete_one({'_id': _id})
        log(getframeinfo(currentframe()), 'Deleted ', str(result))

    def close(self) -> None:
        self.client.close()

    def label_view(self):
        labels = defaultdict(int)
        for article in self.search_label("articles"):
            if article['label'] != article['title']:
                labels[article['label']] += 1
        return labels

    # last is last article index, require is how much articles you need.
    def num_articles(self, col_name: str, last: int, require: int):
        start = time()
        docs = self.db[col_name].find({}).skip(last).limit(require)
        if not docs:
            log(getframeinfo(currentframe()), 'Collection does not exist or empty.')
            return []
        lst = list(docs)
        log(getframeinfo(currentframe()), 'Total : ', str(len(lst)))
        log(getframeinfo(currentframe()), 'Spent time : ', str(time() - start)[0:5], ' secs')
        return lst

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            log(getframeinfo(currentframe()), 'Error type : ', str(exc_type))
            log(getframeinfo(currentframe()), 'Error : ', str(exc_val))
            log(getframeinfo(currentframe()), 'Error tb : \n', ''.join(format_tb(exc_tb)))
        self.client.close()
        log(getframeinfo(currentframe()), 'Database connection closed...')
        return True
