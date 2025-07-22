from pymongo import MongoClient
from config.setting import settings
import os


client = MongoClient(settings.mongo_uri)
collection = client[settings.mongo_db_name][settings.mongo_collection_name]

def query_demographics(user_id: str) -> dict | None:
    user_doc = collection.find_one({"_id": user_id})
    if not user_doc:
        return None
    user_doc.pop("_id", None)
    return {"userID": user_id, **user_doc}