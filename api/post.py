import os

from pymongo import MongoClient

def mongo_init():
    mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

    client = MongoClient(f"mongodb://{mongo_user}:{mongo_pass}@mongodb:27017")
    db = client["collections"]
    collection = db["posts"]
    return collection


def insert_post(collection: MongoClient, post: dict):
    post_id = collection.insert_one(post).inserted_id
    return post_id


def select_post(collection: MongoClient, post_id: str):
    post = collection.find_one({"_id": post_id})
    return post


def select_all_posts(collection: MongoClient):
    all_collection = collection.find()
    return all_collection


def update_post(collection: MongoClient, post_id: str, post: dict):
    updated_post = collection.update_one({"_id": post_id}, {"$set": post})
    return updated_post


def delete_post(collection: MongoClient, post_id: str):
    deleted_post = collection.delete_one({"_id": post_id})
    return deleted_post
