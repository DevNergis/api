from datetime import *
from yt_dlp import YoutubeDL
from io import BytesIO
import dotenv, requests

FILE_PATH = dotenv.get_key(".env", "FILE_PATH")
OPEN_NEIS_API_KEY = dotenv.get_key(".env", "OPEN_NEIS_API_KEY")
YDL_OPTIONS = dotenv.get_key(".env", "YDL_OPTIONS")
HEADERS = dotenv.get_key(".env", "HEADERS")
SERVER_URL = dotenv.get_key(".env", "SERVER_URL")
DATE = datetime.now().strftime('%Y%m%d')

def YDL_URL(url: str):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)

    URL = info['formats'][0]['url']
    return URL

def YDL_cache(URL: str, NAME: str):
    with requests.get(URL, stream=True, headers=HEADERS) as file_request:
        content = BytesIO()
        
        for chunk in file_request.iter_content(chunk_size=1*1024*1024):
            content.write(chunk)

        with open(f"{NAME}", "wb") as file_save:
            file_save.write(content.getbuffer())
        
        content.seek(0)

    return URL, NAME