import requests
import re

OUTPUT_FILE = "playlist.m3u"
COOKIE_FILE = "cookies.txt"

# Load cookies from file
cookies = {}
with open(COOKIE_FILE, "r", encoding="utf-8") as f:
    for line in f:
        if "=" in line:
            k, v = line.strip().split("=", 1)
            cookies[k] = v

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*"
}

playlist = ["#EXTM3U\n"]

# Pages to scan for live couples
SCAN_PAGES = [
    "https://chaturbate.com/couples/?page=1",
    "https://chaturbate.com/couples/?page=2",
    "https://chaturbate.com/couples/?page=3"
]

found_models = set()

# STEP 1: Collect model names
for page in SCAN_PAGES:
    try:
        r = requests.get(page, headers=HEADERS, cookies=cookies, timeout=15)
        if r.status_code != 200:
            continue

        models = re.findall(r'room="([^"]+)"', r.text)
        for m in models:
            found_models.add(m)

    except Exception:
        continue

# STEP 2: Check live status and build stream
for model in sorted(found_models):
    try:
        api = f"https://chaturbate.com/api/chatvideocontext/{model}/"
        r = requests.get(api, headers=HEADERS, cookies=cookies, timeout=15)

        if r.status_code != 200:
            continue

        data = r.json()

        if not data.get("is_broadcasting"):
            continue

        if data.get("broadcast_gender") != "MF":
            continue

        edge = data.get("edge_server")
        stream = data.get("stream_name")

        if not edge or not stream:
            continue

        m3u8 = f"https://{edge}.live.mmcdn.com/live-hls/amlst:{stream}/playlist.m3u8"

        playlist.append(
            f'#EXTINF:-1 group-title="Chaturbate Couple",{model}\n{m3u8}\n'
        )

    except Exception:
        continue

# Write playlist
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(playlist)
