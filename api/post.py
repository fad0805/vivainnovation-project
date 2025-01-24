import os

from pymongo import MongoClient

def mongo_init():
    mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

    client = MongoClient(f"mongodb://{mongo_user}:{mongo_pass}@localhost:27017/")
    return client
