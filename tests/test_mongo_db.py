from pprint import pprint
from pymongo import MongoClient
from utils.db_connector import DBConnector
from utils.init_db import init_empty_mongo_db
import random


def init_test(db_name='test'):
    init_empty_mongo_db(db_name)
    conn = DBConnector(db_name=db_name)

    ids = [1, 13, 24]
    status_types = ["finished", "preparing_for_download", "fail_on_downloading", "converting_to_wav",
                    "fail_on_converting_to_wav", "recognition", "fail_on_recognition", "joining_segments",
                    "downloading",
                    ]
    seed = 42
    random.seed(42)

    gen_parts = []
    for video_id in ids:
        for i in range(10):
            gen_parts.append(
                {
                    'video_id': video_id,
                    "start": 2 * i,
                    "end": 2 * i + 1,
                    "text": f"{13 * i + 17} русский {video_id}"
                }
            )

    gen_status = []
    for video_id in ids:
        gen_status.append(
            {
                "video_id": video_id,
                "status": random.choice(status_types),
                "info": {"1": 1, "2": 2}
            }
        )

    for status in gen_status:
        conn.update_status(status["video_id"], status["status"], status["info"])

    res = conn.get_status_table()
    print("\nStatus table:")
    for el in res:
        print(el)

    conn.insert_parts(gen_parts)

    res = conn.get_parts_table()
    print("\nParts table:")
    for el in res:
        print(el)

    conn.update_status(ids[0], "NEW SUPER STATUS", info={"speed": 424242})

    print(f"\nStatus {ids[0]} video:")
    res = conn.get_status(ids[0])
    print(res)

    print(f"\nParts {ids[0]} video:")
    res = conn.get_parts(ids[0])
    for el in res:
        print(el)

    request_text = "русский"
    print(f"\nFind {request_text} in {ids[0]} video:")
    res = conn.find_text(ids[0], request_text, limit=5)
    for el in res:
        print(el)

    print(f"\nStatus not exists {145421232} video:")
    res = conn.get_status(145421232)
    print(res)

    client = MongoClient()
    client.drop_database(db_name)


if __name__ == '__main__':
    db_con = DBConnector("twitch_speech")

    video_id = '760718196'
    print(f"\nStatus {video_id}:")
    print(db_con.get_status(video_id))

    print(f"\nParts {video_id}")
    parts = db_con.get_parts(video_id)
    for part in parts:
        print(part)

    #res = db_con.get_parts_table()
    #for el in res:
    #    print(el)

    res = db_con.find_text(video_id, "ребята")
    for el in res:
        print(el)
