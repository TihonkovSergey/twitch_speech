import pymongo
from pymongo import MongoClient


def init_empty_mongo_db(db_name):
    client = MongoClient()
    client.drop_database(db_name)

    db = client[db_name]
    status = db['status']
    parts = db['video_parts']

    parts.create_index([('text', 'text')], default_language="russian")
    status.create_index([('video_id', pymongo.ASCENDING)], unique=True)


if __name__ == "__main__":
    init_empty_mongo_db("twitch_speech")
