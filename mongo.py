from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

MONGO_URI = '_'

mongo_client = MongoClient(MONGO_URI, server_api=ServerApi('1'))

db = mongo_client['MyProject']
collection = db['reddit_posts']


def document_exists(query: dict[str, int]) -> bool:
    return db.collection.count_documents(query) > 0
