from fastapi import *
from redis.commands.json.path import Path
import function
import schema

router = APIRouter(prefix="/cipher", tags=["cipher"])


@router.post("/encryption")
async def encryption(body: schema.Encryption):
    return responses.PlainTextResponse(function.Cipher(body.data).encryption())


@router.post("/decryption")
async def decryption(body: schema.Decryption):
    return responses.PlainTextResponse(function.Cipher(body.data).decryption())
