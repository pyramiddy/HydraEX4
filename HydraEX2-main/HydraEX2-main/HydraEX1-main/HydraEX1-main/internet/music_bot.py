import re
from urllib.parse import quote_plus
from youtubesearchpython import VideosSearch

MUSIC_CMD_REGEX = re.compile(r"^/music(?:/|\s+)(.+)$", re.IGNORECASE)

def extract_query(msg: str):
    m = MUSIC_CMD_REGEX.match(msg.strip())
    if m:
        return m.group(1).strip()
    return None

def find_youtube_embed(query: str) -> str | None:
    try:
        vs = VideosSearch(query, limit=1)
        data = vs.result()
        videos = data.get('result', [])
        if not videos:
            return None
        video_id = videos[0]['id']
        return f"https://www.youtube.com/embed/{video_id}?autoplay=1"
    except Exception as e:
        print("Erro na busca:", e)
        return None
