from vod_download_utils.commands import download
from copy import deepcopy

vod_id = '574423677'

default_args = {
    "video": "1234567",
    "quality": "worst",
    "max_workers": 20,
    "start": None,
    "end": None,
    "format": "mkv",
    "keep": False,
    "no_join": False,
    "overwrite": True,
    "path": None,
    "filename": None
}
args = deepcopy(default_args)
args["video"] = vod_id
args["path"] = "data/vods/"
args["filename"] = vod_id

download(args)
