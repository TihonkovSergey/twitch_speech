import os
import config as cf


if __name__ == "__main__":
    wavs_path = '/home/sergey/Documents/homeworks/twitch_speech/data/testing_deepspeech_model/wav/'
    output_path = '/home/sergey/Documents/homeworks/twitch_speech/data/testing_deepspeech_model/output/'
    start_path = cf.START_RECOGNITION_PATH
    os.system('cd {}; python start_recognition.py {} {} -l -dw --time 1'.format(start_path, wavs_path, output_path))
