from utils.video_utils import get_channel_videos, download_video, video2wav
from pprint import pprint
import config as cf


if __name__ == "__main__":
    # Test get channel videos
    channel_id = "voodoosh"  # "test09871234"  # "honeymad"  #
    limit = 1  # some int > 0 or "all"
    sort = "views"  # ["views", "time"]
    type = "highlight"  # ["archive", "highlight", "upload"]
    vods = get_channel_videos(channel_id, limit, sort, type)
    pprint(vods)

    # Test download video
    # '574423677'
    # 812849228 - какие-то школьники
    # 659087312 - voodoosh 25min
    video_id = "812849228"
    path = None  # "testing_download/"
    filename = video_id
    download_video(video_id, path=path, filename=filename)

    # Test mkv to wav
    video2wav(f"{cf.VODS_DIR_PATH}{video_id}.mkv", f"{cf.SOUNDS_DIR_PATH}{video_id}.wav")
