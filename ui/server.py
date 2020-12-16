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


# {'status': 'Ищем видяшку'}
def check_id(video_id):
    status_info = db_connector.get_status(video_id)

    if not status_info:
        return {'status': 'НАЧНИ СКАЧИВАТЬ'}

    status = status_info['status']

    result_string = status + "\n" + "\n".join(f"{key}: {val}" for key, val in status_info["info"].items())
    return {'status': result_string}

def search_text(video_id, input_text):
    data = db_connector.find_text(video_id, input_text)
    result = {}
    for i, sub in enumerate(data):
        timecode = int(sub['start']) // 1000
        text = sub['text']
        result[str(i)] = {'timecode': timecode, 'text': text}
    return result

#return {'0': {'timecode': '00:56', 'text': 'lol chto'},
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

