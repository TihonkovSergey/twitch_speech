from flask import Flask, request, jsonify
from flask_cors import CORS

import sys
sys.path.append("/home/sergey/Documents/homeworks/twitch_speech/")

from utils.main_server import TwitchSpeechServer
from utils.db_connector import DBConnector
import config as cf

pipeline_server = TwitchSpeechServer()
db_connector = DBConnector(cf.DATABASE_NAME)

app = Flask(__name__)
CORS(app)


# {
# 'status': 'Ищем видяшку',
# 'progress': int,
# 'download_speed': str,
# }
def check_id(video_id):
    status_info = db_connector.get_status(video_id)

    if not status_info:
        pipeline_server.process_videos(ids=[video_id])
        return {'status': 'Процесс запущен'}

    status = status_info['status']

    try:
        downloaded_count = int(status_info['info']['downloaded_count'])
        total_count = int(status_info['info']['total_count'])
        progress = int(downloaded_count / total_count) * 100
    except:
        progress = 0

    try:
        download_speed = status_info['info']['speed']
    except:
        download_speed = '-'

    return {
        'status': status,
        'progress': progress,
        'download_speed': download_speed,
    }


def search_text(video_id, input_text):
    if input_text and input_text != '':
        data = db_connector.find_text(video_id, input_text)
    else:
        data = db_connector.get_parts(video_id)
    result = {}
    for i, sub in enumerate(data):
        timecode = int(sub['start']) // 1000
        text = sub['text']
        result[str(i)] = {'timecode': timecode, 'text': text}
    return result


# return {'0': {'timecode': '00:56', 'text': 'lol chto'},
#        '1': {'timecode': '02:56', 'text': 'lol kek'}}


@app.route('/', methods=['GET'])
def check():
    return check_id(request.args.get('video_id'))


@app.route('/search', methods=['GET'])
def search():
    video_id, input_text = request.args.get('video_id'), request.args.get('input_text')
    return search_text(video_id, input_text)


if __name__ == "__main__":
    app.run(debug=True)
