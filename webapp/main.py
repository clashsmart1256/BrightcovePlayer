import os
import requests
from flask import Flask
from flask import render_template
from config import Config
from base64 import standard_b64encode, standard_b64decode

ACCOUNT_ID = os.environ.get("ACCOUNT_ID", Config.ACCOUNT_ID)
BCOV_POLICY = os.environ.get("BCOV_POLICY", Config.BCOV_POLICY)

bc_url = f"https://edge.api.brightcove.com/playback/v1/accounts/{ACCOUNT_ID}/videos"

bc_hdr = {"BCOV-POLICY": BCOV_POLICY}

app = Flask(__name__)


def str_to_b64(__str: str) -> str:
    str_bytes = __str.encode('ascii')
    bytes_b64 = standard_b64encode(str_bytes)
    b64 = bytes_b64.decode('ascii')
    return b64


def b64_to_str(b64: str) -> str:
    bytes_b64 = b64.encode('ascii')
    bytes_str = standard_b64decode(bytes_b64)
    __str = bytes_str.decode('ascii')
    return __str


@app.route("/encode")
def encoder_():
    try:
        video_url = request.args['id']
    except Exception as e:
        edata = "Please parse ?id= when calling the api"
        return edata
    video_url = str_to_b64(video_url)
    return {"encoded": video_url}


@app.route("/<int(fixed_digits=13):video_id>")
def index(video_id):
    try:
        video_id = b64_to_str(video_id)
    except:
        return "<font color=red size=15>Wrong Video ID</font> <br> ask at @JV_Community in Telegram"
    video_response = requests.get(f"{bc_url}/{video_id}", headers=bc_hdr)

    if video_response.status_code != 200:
        return "<font color=red size=20>Wrong Video ID</font>"

    video = video_response.json()

    video_name = video["name"]

    video_source = video["sources"][3]
    video_url = video_source["src"]
    widevine_url = ""
    microsoft_url = ""
    if "key_systems" in video_source:
        widevine_url = video_source["key_systems"]["com.widevine.alpha"]["license_url"]
        microsoft_url = video_source["key_systems"]["com.microsoft.playready"]["license_url"]
    track_url = video["text_tracks"][1]["src"]
    return render_template(
        "template.html",
        video_name=video_name,
        video_url=video_url,
        track_url=track_url,
        widevine_url=widevine_url,
        microsoft_url=microsoft_url,
    )
