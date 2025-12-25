import requests

MODELS_FILE = "models.txt"
OUTPUT_FILE = "playlist.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

playlist = ["#EXTM3U\n"]

with open(MODELS_FILE) as f:
    models = [m.strip() for m in f if m.strip()]

for model in models:
    try:
        url = f"https://chaturbate.com/api/chatvideocontext/{model}/"
        r = requests.get(url, headers=HEADERS, timeout=10)

        if r.status_code != 200:
            continue

        data = r.json()

        if not data.get("is_broadcasting"):
            continue

        if not data.get("is_couple"):
            continue

        edge = data["edge_server"]
        stream = data["stream_name"]
        m3u8 = f"https://{edge}.live.mmcdn.com/live-hls/amlst:{stream}/playlist.m3u8"

        playlist.append(
            f'#EXTINF:-1 group-title="Chaturbate Couple",{model}\n{m3u8}\n'
        )

    except Exception:
        pass

with open(OUTPUT_FILE, "w") as f:
    f.writelines(playlist)
