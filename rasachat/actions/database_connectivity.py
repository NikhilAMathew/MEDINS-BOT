from pymongo import MongoClient

def connect_to_mongodb():
    client = MongoClient("mongodb://username:password@localhost:27017/db_name")
    db = client['rasa']
    return db
