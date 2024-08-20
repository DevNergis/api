from datetime import *
from io import BytesIO
import dotenv
import redis.asyncio as redis
import requests
from yt_dlp import YoutubeDL
from pytz import timezone
from typing import *
import hashlib
import secrets
import hmac
import base64

FILE_PATH = dotenv.get_key(".env", "FILE_PATH")
OPEN_NEIS_API_KEY = dotenv.get_key(".env", "OPEN_NEIS_API_KEY")
YDL_OPTIONS = dotenv.get_key(".env", "YDL_OPTIONS")
HEADERS = dotenv.get_key(".env", "HEADERS")
SERVER_URL = dotenv.get_key(".env", "SERVER_URL")
DATE = datetime.now(timezone('Asia/Seoul')).strftime('%Y%m%d')
N_DATE = datetime.now(timezone('Asia/Seoul')).strftime('%Y%m%d') + timedelta(days=1)
DATE_QLOAT = datetime.now()
QLOAT_PASSWORD = dotenv.get_key(".env", "QLOAT_PASSWORD")
FILE_PATH_QLOAT = dotenv.get_key(".env", "FILE_PATH_QLOAT")
FOLDER_PATH = dotenv.get_key(".env", "FOLDER_PATH")

DB = dotenv.get_key(".env", "DB")
FILE_DB = dotenv.get_key(".env", "FILE_DB")
PASSWORD_DB = dotenv.get_key(".env", "PASSWORD_DB")

FOLDER_DB = dotenv.get_key(".env", "FOLDER_DB")
SALT_DB = dotenv.get_key(".env", "SALT_DB")

x_agent_did = dotenv.get_key(".env", "x-agent-did")
Authorization = dotenv.get_key(".env", "Authorization")


class Security:
    def __init__(self, password: str, salt: bytes = None, password_hash: bytes = None, algorithm: str = 'sha3_256',
                 iterations: int = 100000, dklen: Optional[int] = None, to_hex: bool = False) -> None:
        self.password = password.encode("utf-8")
        self.salt = salt
        self.password_hash = password_hash
        self.algorithm = algorithm
        self.iterations = iterations
        self.dklen = dklen
        self.to_hex = to_hex

    def hash_new_password(self) -> Tuple[bytes, bytes] | Tuple[str, str]:
        salt = secrets.token_bytes(16)
        password_hash = hashlib.pbkdf2_hmac(self.algorithm, self.password, salt, self.iterations, self.dklen)
        if self.to_hex:
            return salt.hex(), password_hash.hex()
        else:
            return salt, password_hash

    def is_correct_password(self) -> bool:
        return hmac.compare_digest(self.password_hash,
                                   hashlib.pbkdf2_hmac(self.algorithm, self.password, self.salt, self.iterations,
                                                       self.dklen))


class Obfuscation:
    def __init__(self, data: str):
        self.data = data

    def on(self):
        return base64.b85encode(self.data.encode()).hex()

    def off(self):
        return base64.b85decode(bytes.fromhex(self.data).decode()).decode()

    def hexoff(self):
        return bytes.fromhex(self.data)


def pool(db_num: int = 0):
    return redis.ConnectionPool().from_url(f"{DB}/{db_num}")


def ydl_url(url: str):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)

    url = info['formats'][0]['url']
    return url


# noinspection PyTypeChecker
def ydl_cache(url: str, name: str):
    with requests.get(url, stream=True, headers=HEADERS) as file_request:
        content = BytesIO()

        for chunk in file_request.iter_content(chunk_size=1 * 1024 * 1024):
            content.write(chunk)

        with open(f"{name}", "wb") as file_save:
            file_save.write(content.getbuffer())

        content.seek(0)

    return url, name
