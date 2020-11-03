from vod_download_utils.commands import videos
from copy import deepcopy
import os

channel_name = "test09871234"

default_args = {
    "channel_name": "1234567",
    "game": [],
    "limit": 100,
    "sort": "time",  # ["views", "time"]
    "type": "archive",  # ["archive", "highlight", "upload"],
    "pager": False,  # If there are more results than LIMIT, ask to show next page",
    "path": "data/",
    "filename": "1234567.txt"
}
args = deepcopy(default_args)
args["channel_name"] = channel_name
args["path"] = "data/vod_list/"
args["filename"] = channel_name + ".txt"

full_filename = args["path"] + args["filename"]
if os.path.exists(full_filename):
    os.remove(full_filename)

videos(args)
