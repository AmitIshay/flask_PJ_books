from bson import json_util 
from pymongo import MongoClient

def import_json_to_mongo(json_path, db_name, collection_name, mongo_uri="mongodb://localhost:27017"):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    # Optional: Clear old data
    collection.delete_many({})

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json_util.loads(f.read()) 

        if isinstance(data, list):
            collection.insert_many(data)
        else:
            collection.insert_one(data)

    print(f"Data imported into {db_name}.{collection_name}")

# Usage
import_json_to_mongo("books.json", "bookgrocer", "books")
import_json_to_mongo("users.json", "bookgrocer", "users")

