import hashlib
import uuid
import base64

import fastapi
from fastapi import *
import redis.asyncio as redis
from redis.commands.json.path import Path

from src import function, schema

router = APIRouter(prefix="/folder", tags=["folder"], default_response_class=responses.ORJSONResponse)


@router.post("/make")
async def folder_make(body: schema.FolderMake):
    DB = await redis.Redis(connection_pool=function.pool(function.FOLDER_DB))

    folder_uuid = str(uuid.uuid4())
    key = hashlib.md5(body.folder_name.encode() + folder_uuid.encode()).hexdigest()
    folder_name = base64.b85encode(body.folder_name.encode()).hex()

    if body.folder_password is None:
        folder_password = None
    else:
        DB_SALT = await redis.Redis(connection_pool=function.pool(function.SALT_DB))
        salt, folder_password = function.Security(body.folder_password, to_hex=True).hash_new_password()

        await DB_SALT.json().set(folder_uuid.encode().hex(), Path.root_path(), {"folder_salt": salt})
        await DB_SALT.close()

    await DB.json().set(key, Path.root_path(), {
        "folder_uuid": folder_uuid.encode().hex(),
        "folder_name": folder_name,
        "folder_password": folder_password,
        "folder_contents": None
    })

    return {"folder_id": key, "folder_name": body.folder_name, "folder_url": f"{function.SERVER_URL}/v2/folder/{key}"}


@router.get("/{folder_id}")
async def folder_open(folder_id: str):
    return {"folder_id": folder_id}
