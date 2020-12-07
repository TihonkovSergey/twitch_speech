import config as cf
import os


if __name__ == '__main__':
    wavs_path = '/home/sergey/Documents/homeworks/twitch_speech/data/testing_deepspeech_model/wav/'  # cf.SOUNDS_DIR_PATH
    output_path = '/home/sergey/Documents/homeworks/twitch_speech/data/testing_deepspeech_model/output/'  # cf.RECOGNITION_RESULTS_DIR_PATH
    start_path = cf.START_RECOGNITION_PATH
    serve_freq = cf.RECOGNITION_SERVE_FREQ

    # Start serve
    os.system('cd {}; python start_recognition.py {} {} -l -dw --time {}'
              .format(start_path, wavs_path, output_path, serve_freq))
