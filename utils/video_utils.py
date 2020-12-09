import m3u8
import re
import requests
import tempfile
import os
import unicodedata
import subprocess
import shutil
from urllib.parse import urlparse
from pathlib import Path
from twitch import twitch
from twitch.download import download_files
import config as cf

VIDEO_PATTERNS = [
    r"^(?P<id>\d+)?$",
    r"^https://(www.)?twitch.tv/videos/(?P<id>\d+)(\?.+)?$",
]


def video2wav(path_in, path_out, hz=8000):
    if not os.path.exists(path_in):
        raise FileNotFoundError(f"File not found on {path_in}")

    path_list = path_out.split("/")
    path = "/".join(path_list[:-1])

    if not os.path.exists(path):
        os.makedirs(path)

    os.system('ffmpeg -i {} -ac 1 -ar {} -vn {} -y || exit'.format(path_in, hz, path_out))
    # -ac 1 mono channel
    # -ar 8000 Hz


def get_channel_videos(channel_id, limit="all", sort="time", video_type="archive"):
    videos = []
    if limit == "all":
        limit = int(twitch.get_channel_videos(channel_id, 1, sort, video_type)["totalCount"])
        if limit == 0:
            limit = 1

    cursor = None
    n = limit
    while n > 0:
        curr_size = min(n, 100)
        data = twitch.get_channel_videos(channel_id, curr_size, sort, video_type, after=cursor)
        has_next_page = data["pageInfo"]["hasNextPage"]
        cursor = data["edges"][-1]["cursor"] if has_next_page else None

        videos += data["edges"]
        n -= curr_size
        if not has_next_page:
            break

    return {
        "videos": videos,
        "totalCount": len(videos)
    }


def download_video(video_id, quality="worst", workers=20,
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
    path_map = download_files(base_uri, target_dir, vod_paths, workers)

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


def _parse_playlists(playlists_m3u8):
    playlists = m3u8.loads(playlists_m3u8)

    for p in playlists.playlists:
        name = p.media[0].name if p.media else ""
        resolution = "x".join(str(r) for r in p.stream_info.resolution)
        yield name, resolution, p.uri


def _get_playlist_by_name(playlists, quality):
    if quality == "source":
        _, _, uri = playlists[0]
        return uri

    if quality == 'worst':
        _, _, uri = playlists[-1]
        return uri

    for name, _, uri in playlists:
        if name == quality:
            return uri

    available = ", ".join([name for (name, _, _) in playlists])
    msg = "Quality '{}' not found. Available qualities are: {}." \
          " Also maybe you want 'source' or 'worst'".format(quality, available)
    raise ValueError(msg)


def _crete_temp_dir(base_uri):
    """Create a temp dir to store downloads if it doesn't exist."""
    path = urlparse(base_uri).path.lstrip("/")
    temp_dir = Path(tempfile.gettempdir(), "twitch-dl", path)
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def _get_vod_paths(playlist):
    """Extract unique VOD paths for download from playlist."""
    files = []
    for segment in playlist.segments:
        if segment.uri not in files:
            files.append(segment.uri)

    return files


def _slugify(value):
    re_pattern = re.compile(r'[^\w\s-]', flags=re.U)
    re_spaces = re.compile(r'[-\s]+', flags=re.U)
    value = str(value)
    value = unicodedata.normalize('NFKC', value)
    value = re_pattern.sub('', value).strip().lower()
    return re_spaces.sub('_', value)


def _video_target_filename(video, video_format="mkv", path=None, filename=None):
    if filename:
        name = filename + "." + video_format
    else:
        match = re.search(r"^(\d{4})-(\d{2})-(\d{2})T", video['published_at'])
        date = "".join(match.groups())

        name = "_".join([
            date,
            video['_id'][1:],
            video['channel']['name'],
            _slugify(video['title']),
        ])

        name = name + "." + video_format

    full_path = cf.VODS_DIR_PATH
    if path:
        full_path += path

    if not os.path.exists(full_path):
        os.makedirs(full_path)

    name = full_path + name
    return name


def _join_vods(playlist_path, target):
    command = [
        "ffmpeg",
        "-i", playlist_path,
        "-c", "copy",
        target,
        "-stats",
        "-loglevel", "warning",
        "-y",
    ]

    result = subprocess.run(command, stderr=subprocess.STD_ERROR_HANDLE, stdout=subprocess.STD_ERROR_HANDLE)
    if result.returncode != 0:
        raise SystemError("Joining files failed")
