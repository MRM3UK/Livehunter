import requests

MODELS_FILE = "models.txt"
OUTPUT_FILE = "playlist.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

playlist = ["#EXTM3U\n"]

with open(MODELS_FILE, "r", encoding="utf-8") as f:
    models = [line.strip() for line in f if line.strip()]

for model in models:
    try:
        url = f"https://chaturbate.com/api/chatvideocontext/{model}/"
        r = requests.get(url, headers=HEADERS, timeout=10)

        if r.status_code != 200:
            continue

        data = r.json()

        # Must be LIVE
        if not data.get("is_broadcasting"):
            continue

        # Must be COUPLE (MF)
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

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(playlist)
