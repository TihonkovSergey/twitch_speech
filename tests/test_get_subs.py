import pysubs2
import json
from pprint import pprint
from utils.video_utils import get_video_subs

if __name__ == '__main__':
    SUBS_PATH = '/home/sergey/Documents/homeworks/twitch_speech/data/testing_deepspeech_model/output/ass/'
    video_id = '659087312'

    subs = get_video_subs(video_id, subs_path=SUBS_PATH)

    print(type(subs))
    pprint(subs)
