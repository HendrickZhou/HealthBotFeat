from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://root:secret@localhost:27017")
DB_NAME = "demographic"
COLLECTION_NAME = "users"

client = MongoClient(MONGO_URI)
collection = client[DB_NAME][COLLECTION_NAME]

def query_demographics(user_id: str) -> dict | None:
    user_doc = collection.find_one({"_id": user_id})
    if not user_doc:
        return None
    user_doc.pop("_id", None)
    return {"user_id": user_id, **user_doc}