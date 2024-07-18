import hashlib
import uuid
import base64

import fastapi
from fastapi import *
import aioredis as redis
from redis.commands.json.path import Path

router = APIRouter(prefix="/file", tags=["file"], default_response_class=responses.ORJSONResponse)


@router.get("/folder/make")
async def __asdadfolder_make():
    return "asdasd"
