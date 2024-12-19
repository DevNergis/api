import base64
import hashlib
import hmac
import random
import secrets
import zlib
from datetime import *
from typing import *

import orjson
import redis.asyncio as redis
import toml
from pytz import timezone


def generate_user_agent():
    """Random User-Agent

    Returns:
        User-Agent
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36",
    ]
    return random.choice(user_agents)


HEADERS = headers = {"User-Agent": generate_user_agent()}
DATE = datetime.now(timezone("Asia/Seoul")).strftime("%Y%m%d")
N_DATE = (datetime.now(timezone("Asia/Seoul")) + timedelta(days=1)).strftime("%Y%m%d")
DATE_QLOAT = datetime.now()
YDL_OPTIONS = {
    "netrc": "$HOME/.netrc",
    "format": "bestaudio/best",
    "audio_format": "flac",
    "audio_quality": "0",
    "extract_audio": "True",
    "noplaylist": "True",
    "no_warnings": "True",
}

# Load the TOML configuration file
config = toml.load("config.toml")

# Access the configuration values
FILE_PATH = config["File"]["FILE_PATH"]
OPEN_NEIS_API_KEY = config["Key"]["OPEN_NEIS_API_KEY"]
SERVER_URL = config["Env"]["SERVER_URL"]
QLOAT_PASSWORD = config["Key"]["QLOAT_PASSWORD"]
FILE_PATH_QLOAT = config["File"]["FILE_PATH_QLOAT"]
FOLDER_PATH = config["File"]["FOLDER_PATH"]
DB = config["DB"]["URL"]
FILE_DB = config["DB"]["FILE_DB"]
PASSWORD_DB = config["DB"]["PASSWD_DB"]
FOLDER_DB = config["DB"]["FOLDER_DB"]
SALT_DB = config["DB"]["SALT_DB"]
x_agent_did = config["Key"]["x-agent-did"]
Authorization = config["Key"]["Authorization"]


class HashingUtility:
    def __init__(
        self,
        password: str,
        salt: bytes = None,
        password_hash: bytes = None,
        algorithm: str = "sha3_256",
        iterations: int = 100000,
        dklen: Optional[int] = None,
        to_hex: bool = False,
    ) -> None:
        self.password = password.encode("utf-8")
        self.salt = salt
        self.password_hash = password_hash
        self.algorithm = algorithm
        self.iterations = iterations
        self.dklen = dklen
        self.to_hex = to_hex

    def hash_new_password(self) -> Tuple[bytes, bytes] | Tuple[str, str]:
        salt = secrets.token_bytes(16)
        password_hash = hashlib.pbkdf2_hmac(
            self.algorithm, self.password, salt, self.iterations, self.dklen
        )
        if self.to_hex:
            return salt.hex(), password_hash.hex()
        else:
            return salt, password_hash

    def is_correct_password(self) -> bool:
        return hmac.compare_digest(
            self.password_hash,
            hashlib.pbkdf2_hmac(
                self.algorithm, self.password, self.salt, self.iterations, self.dklen
            ),
        )


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


class Cipher:
    def __init__(self, data: str):
        self.data = data

    def encryption(self):
        return zlib.compress(
            base64.b85encode(
                base64.a85encode(
                    base64.b16encode(
                        base64.b32encode(base64.b64encode(self.data.encode()))
                    )
                )
            ),
            9,
        ).hex()

    def decryption(self):
        return base64.b64decode(
            base64.b32decode(
                base64.b16decode(
                    base64.a85decode(
                        base64.b85decode(zlib.decompress(bytes.fromhex(self.data)))
                    )
                )
            )
        ).decode()


# noinspection SpellCheckingInspection,PyPep8Naming,PyMethodParameters
class aiorjson:
    async def dumps(
        obj: Any,
        default: Optional[Callable[[Any], Any]] = None,
        option: Optional[int] = None,
    ):
        return orjson.dumps(obj, default, option)

    async def loads(obj: Union[bytes, bytearray, memoryview, str]):
        return orjson.loads(obj)
