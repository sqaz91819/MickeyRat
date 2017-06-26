import pymongo
from .crawler import article_info
from pymongo import MongoClient
from pymongo import collection

art1 = article_info("https://www.ptt.cc/bbs/movie/M.1498371150.A.FDE.html")
art2 = article_info("https://www.ptt.cc/bbs/movie/M.1498380389.A.5D6.html")

# create database
# collection.Collection(database, "namestring", create=True)
client = MongoClient('localhost', 27017)
db = client.test
result = db.articles.insert_one(art1)
print(result.inserted_id)
