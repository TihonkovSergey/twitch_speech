from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

idx = 0
answer = [{'status': 'Ищем видяшку', 'text': '', 'id': 827901857},
          {'status': 'Загружаем', 'text': '', 'id': 827901857},
          {'status': 'success', 'text': 'abcdefghijklmnop',  'id': 827901857}] 
          
# {'status': 'Ищем видяшку'}
def check_id(id):
    global idx
    if (idx < len(answer)):
        idx += 1
        return answer[idx - 1]
    else:
        idx = 0
        return check_id(id)

def search_text(video_id, input_text):
    return {'0': {'timecode': '00:56', 'text': 'lol chto'},
            '1': {'timecode': '02:56', 'text': 'lol kek'}}


@app.route('/', methods=['GET'])
def check():
    return check_id(request.args.get('video_id'))

@app.route('/search', methods=['GET'])
def search():
    video_id, input_text = request.args.get('video_id'), request.args.get('input_text')
    return search_text(video_id, input_text)

if __name__ == "__main__":
     app.run(debug=True)

