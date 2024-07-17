import hashlib
import uuid
import base64

from src import func2
from fastapi import *
import redis.asyncio as redis
from redis.commands.json.path import Path

from src import function, schema

router = APIRouter(prefix="/cipher", tags=["cipher"])


@router.post("/encryption")
async def encryption(body: schema.Encryption):
    return responses.PlainTextResponse("===" + func2.Cipher(body.data).encryption() + "===")
