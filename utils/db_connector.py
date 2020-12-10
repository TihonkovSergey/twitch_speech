from pymongo import MongoClient


class DBConnector:
    def __init__(self, db_name):
        self.db = MongoClient()[db_name]
        self.status = self.db['status']
        self.parts = self.db['video_parts']

    def update_status(self, video_id, status, info=None):
        res = self.get_status(video_id)
        data = {
            "video_id": video_id,
            "status": status,
        }
        if info:
            data['info'] = info

        if res:
            data = {
                "$set": data
            }
            self.status.update_one({"video_id": video_id}, data)
        else:
            self.status.insert_one(data)

    def get_status(self, video_id):
        res = self.status.find_one({'video_id': video_id})
        return res

    def find_text(self, video_id, request_text, limit=None):
        aggregate_pipeline = [
            {
                "$match": {"video_id": video_id, "$text": {"$search": request_text}}
            },
            {
                "$sort": {"score": {"$meta": "textScore"}}
            },
        ]
        if limit:
            aggregate_pipeline.append({"$limit": limit})

        result = self.parts.aggregate(aggregate_pipeline)
        return list(result)

    def insert_parts(self, parts):
        if parts:
            self.parts.insert_many(parts)
        else:
            raise ValueError("Parts are empty!")

    def get_parts(self, video_id):
        res = self.parts.find({"video_id": video_id})
        return list(res)

    def get_status_table(self):
        res = self.status.find()
        return list(res)

    def get_parts_table(self):
        res = self.parts.find()
        return list(res)

    def delete_video(self, video_id):
        self.status.delete_many({"video_id": video_id})
        self.parts.delete_many({"video_id": video_id})


if __name__ == '__main__':
    pass
