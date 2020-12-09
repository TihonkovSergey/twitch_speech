from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Thread
import time
from functools import partial
from collections import OrderedDict, defaultdict
from datetime import datetime
import m3u8
import re
import requests
import os
import shutil
from twitch import twitch
from twitch.utils import format_size, format_duration
import config as cf
from utils.video_utils import _parse_playlists, _get_playlist_by_name, _crete_temp_dir, \
    _video_target_filename, _get_vod_paths, _join_vods, video2wav, get_video_subs, recognize
from twitch.download import download_file

VIDEO_PATTERNS = [
    r"^(?P<id>\d+)?$",
    r"^https://(www.)?twitch.tv/videos/(?P<id>\d+)(\?.+)?$",
]

"""
{
    'id': {
        'status': 'download_finished',
        'download_info': {
            'total_count': total_count,
            'downloaded_count': downloaded_count,
            'downloaded_size': format_size(downloaded_size),
            'est_total_size': format_size(est_total_size),
            'speed': format_size(speed) if speed > 0 else "-",
            'remaining': format_duration(remaining) if speed > 0 else "-",
        }
        
    }
}

"""


class TwitchSpeechServer:
    def __init__(self):
        self.db_connector = None
        self.video_status = defaultdict()

    def process_videos(self, ids, workers=20):
        for video_id in ids:
            self.video_status[video_id] = {
                'status': 'preparing_for_download',
                'download_info': {},
            }

        partials = (partial(self._process_video, i, workers=workers) for i in ids)
        threads = [Thread(target=fn) for fn in partials]
        for th in threads:
            th.start()

    def _process_video(self, video_id, workers):
        #  download
        try:
            self._download_video(video_id, workers=workers,  filename=video_id)
        except:
            self.video_status[video_id]['status'] = 'fail_on_downloading'
            return

        #  mkv2wav
        self.video_status[video_id]['status'] = 'converting_to_wav'
        try:
            video2wav(f"{cf.VODS_DIR_PATH}{video_id}.mkv", f"{cf.SOUNDS_DIR_PATH}{video_id}.wav")
            # delete video
        except:
            # delete wav if exist
            self.video_status[video_id]['status'] = 'fail_on_converting_to_wav'
            return

        # recognition
        self.video_status[video_id]['status'] = 'recognition'
        try:
            recognize(video_id, cf.START_RECOGNITION_PATH, cf.SOUNDS_DIR_PATH, cf.RECOGNITION_RESULTS_DIR_PATH)
        except:
            self.video_status[video_id]['status'] = 'fail_on_recognition'
            return

        self.video_status[video_id]['status'] = 'finished'
        # push in db
        return self.get_video_subs(video_id)

    def get_video_status(self, video_id):
        return self.video_status[video_id]

    def _download_video(self, video_id, quality="worst", workers=20,
                        video_format="mkv", path=None, filename=None):
        # Matching video_id
        match = None
        for pattern in VIDEO_PATTERNS:
            match = re.match(pattern, video_id)
            if match:
                break
        if not match:
            raise ValueError(f"Invalid video: {video_id}")

        video_id = match.group('id')

        # Looking up video
        video = twitch.get_video(video_id)

        # Fetching access token
        access_token = twitch.get_access_token(video_id)

        # Fetching playlists
        playlists_m3u8 = twitch.get_playlists(video_id, access_token)
        playlists = list(_parse_playlists(playlists_m3u8))
        playlist_uri = (_get_playlist_by_name(playlists, quality))

        # Fetching playlist
        response = requests.get(playlist_uri)
        response.raise_for_status()
        playlist = m3u8.loads(response.text)

        base_uri = re.sub("/[^/]+$", "/", playlist_uri)
        target_dir = _crete_temp_dir(base_uri)
        vod_paths = _get_vod_paths(playlist)

        # Save playlists for debugging purposes
        with open(os.path.join(target_dir, "playlists.m3u8"), "w") as f:
            f.write(playlists_m3u8)
        with open(os.path.join(target_dir, "playlist.m3u8"), "w") as f:
            f.write(response.text)

        # Downloading VODs to target_dir
        path_map = self._download_files(video_id, base_uri, target_dir, vod_paths, workers)
        self.video_status[video_id]['status'] = 'joining_segments'

        # Make a modified playlist which references downloaded VODs
        # Keep only the downloaded segments and skip the rest
        org_segments = playlist.segments.copy()
        playlist.segments.clear()
        for segment in org_segments:
            if segment.uri in path_map:
                segment.uri = path_map[segment.uri]
                playlist.segments.append(segment)

        playlist_path = os.path.join(target_dir, "playlist_downloaded.m3u8")
        playlist.dump(playlist_path)

        # Joining files
        target = _video_target_filename(video, video_format, path=path, filename=filename)
        _join_vods(playlist_path, target)

        # Deleting temporary files
        shutil.rmtree(target_dir)

    def _download_files(self, video_id, base_url, target_dir, vod_paths, max_workers):
        """
        Downloads a list of VODs defined by a common `base_url` and a list of
        `vod_paths`, returning a dict which maps the paths to the downloaded files.
        """
        self.video_status[video_id]['status'] = 'downloading'

        urls = [base_url + path for path in vod_paths]
        targets = [os.path.join(target_dir, "{:05d}.ts".format(k)) for k, _ in enumerate(vod_paths)]
        partials = (partial(download_file, url, path) for url, path in zip(urls, targets))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            start_time = datetime.now()

            # run download
            futures = [executor.submit(fn) for fn in partials]

            downloaded_count = 0
            downloaded_size = 0
            total_count = len(futures)
            for future in as_completed(futures):
                size = future.result()
                downloaded_count += 1
                downloaded_size += size

                est_total_size = int(total_count * downloaded_size / downloaded_count)
                duration = (datetime.now() - start_time).seconds
                speed = downloaded_size // duration if duration else 0
                remaining = (total_count - downloaded_count) * duration / downloaded_count

                info = {
                    'total_count': total_count,
                    'downloaded_count': downloaded_count,
                    'downloaded_size': format_size(downloaded_size),
                    'est_total_size': format_size(est_total_size),
                    'speed': format_size(speed) if speed > 0 else "-",
                    'remaining': format_duration(remaining) if speed > 0 else "-",
                }
                self.video_status[video_id]['download_info'] = info

        return OrderedDict(zip(vod_paths, targets))

    def get_video_subs(self, video_id):
        return get_video_subs(video_id, subs_path=cf.SUBS_DIR_PATH)


if __name__ == '__main__':
    # Example
    server = TwitchSpeechServer()

    videos = ['760718196', '574423677', '658442340']
    server.process_videos(videos)

    for _ in range(30):
        for video_id in videos:
            tmp = server.get_video_status(video_id)
            status = tmp['status']
            info = tmp['download_info']
            print(f'Video {video_id}:\nStatus: {status}\nInfo: {info}\n\n')

        time.sleep(5)
