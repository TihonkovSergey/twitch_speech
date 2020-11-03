import os


def video2wav(path_in, path_out):
    if not os.path.exists(path_in):
        raise FileNotFoundError()

    path_list = path_out.split("/")
    path = "/".join(path_list[:-1])
    print(path)
    if not os.path.exists(path):
        os.makedirs(path)

    os.system('ffmpeg -i {} -vn {} || exit'.format(path_in, path_out))


if __name__ == "__main__":
    video2wav("../data/vods/574423677.mkv", "../data/sounds/574423677.wav")
