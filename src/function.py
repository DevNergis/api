from datetime import *
import dotenv
import orjson
import redis.asyncio as redis
from pytz import timezone
from typing import *
import hashlib
import secrets
import hmac
import base64
import base64
import zlib
import httpx
import redis.asyncio as aioredis

FILE_PATH = dotenv.get_key(".env", "FILE_PATH")
OPEN_NEIS_API_KEY = dotenv.get_key(".env", "OPEN_NEIS_API_KEY")
YDL_OPTIONS = dotenv.get_key(".env", "YDL_OPTIONS")
HEADERS = dotenv.get_key(".env", "HEADERS")
SERVER_URL = dotenv.get_key(".env", "SERVER_URL")
DATE = datetime.now(timezone('Asia/Seoul')).strftime('%Y%m%d')
N_DATE = (datetime.now(timezone('Asia/Seoul')) + timedelta(days=1)).strftime('%Y%m%d')
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


class Redis(aioredis.Redis):
    async def __init__(self, db_num: str):
        await super(connection_pool=await Redis.pool(db_num))

    async def pool(db_num: int = 0):
        return await aioredis.ConnectionPool().from_url(f"{DB}/{db_num}")


class Cipher:
    def __init__(self, data: str):
        self.data = data

    def encryption(self):
        return zlib.compress(base64.b85encode(
            base64.a85encode(base64.b16encode(
                base64.b32encode(base64.b64encode(
                    self.data.encode()))))), 9).hex()

    def decryption(self):
        return base64.b64decode(
            base64.b32decode(base64.b16decode(
                base64.a85decode(base64.b85decode(
                    zlib.decompress(bytes.fromhex(self.data))))))).decode()

class HTTPRequest(httpx.AsyncClient):
    async def __init__(self, **kwargs):
        await super.__init__(http2=True, **kwargs)


class aiorjson():
    async def dumps(self, obj: Any, default: Optional[Callable[[Any], Any]] = None, option: Optional[int] = None):
        orjson.dumps(obj, default, option)

    async def loads(self, obj: Union[bytes, bytearray, memoryview, str]):
        orjson.loads(obj)
