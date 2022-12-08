from pymongo import MongoClient
import os
DATABASE_URL = "mongodb+srv://test:test@test.eathjzx.mongodb.net/?retryWrites=true&w=majority"
DATABASE_URL = os.environ.get("DATABASE_URL", DATABASE_URL)


def get_database():
   client = MongoClient(DATABASE_URL)
   return client['test']

def get_collection(name='tasks'):
    dbname = get_database()
    collection = dbname["tasks"]
    return collection