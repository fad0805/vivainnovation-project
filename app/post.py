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
    last_post = collection.find_one(sort=[("_id", -1)])
    post["id"] = 1
    if last_post:
        post["id"] = last_post["id"] + 1
    result = collection.insert_one(post)
    post_id = ''
    if result.acknowledged:
        post_id = post["id"]
    return post_id


def select_post(collection: MongoClient, post_id: int):
    post = collection.find_one({"id": post_id})
    return post


def select_all_posts(
        collection: MongoClient, page: int, page_size: int, author_id: str
):
    filter = {} if not author_id else {"author_id": author_id}
    all_posts = collection.find(filter, {"_id": 0})\
        .sort("_id", -1).skip((page - 1) * page_size).limit(page_size)
    return all_posts.to_list()


def update_post(collection: MongoClient, post_id: int, post: dict):
    updated_post = collection.update_one({"id": post_id}, {"$set": post})
    return updated_post


def delete_post(collection: MongoClient, post_id: int):
    deleted_post = collection.delete_one({"id": post_id})
    return deleted_post
