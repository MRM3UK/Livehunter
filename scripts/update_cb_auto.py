import requests
import re
import os

OUTPUT_FILE = "playlist.m3u"
COOKIE_FILE = "cookies.txt"

# Check cookie file exists
if not os.path.exists(COOKIE_FILE):
    print("cookies.txt not found")
    with open(OUTPUT_FILE, "w") as f:
        f.write("#EXTM3U\n")
    exit(0)

# Load cookies safely
cookies = {}
with open(COOKIE_FILE, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        line = line.strip()
        if "=" in line:
            k, v = line.split("=", 1)
            cookies[k] = v

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*"
}

playlist = ["#EXTM3U\n"]

SCAN_PAGES = [
    "https://chaturbate.com/couples/?page=1",
    "https://chaturbate.com/couples/?page=2"
]

found_models = set()

# Step 1: scrape couple pages
for page in SCAN_PAGES:
    try:
        r = requests.get(page, headers=HEADERS, cookies=cookies, timeout=20)
        if r.status_code != 200:
            continue

        models = re.findall(r'room="([^"]+)"', r.text)
        found_models.update(models)
    except Exception as e:
        print("Scan error:", e)

# Step 2: check live status
for model in sorted(found_models):
    try:
        api = f"https://chaturbate.com/api/chatvideocontext/{model}/"
        r = requests.get(api, headers=HEADERS, cookies=cookies, timeout=20)

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
    except Exception as e:
        print("Model error:", model, e)

# Write playlist (always)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(playlist)
