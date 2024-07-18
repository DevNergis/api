import hashlib
import uuid
import base64

import aiofiles
import fastapi.responses
import ujson

from typing import *
from fastapi import *
from fastapi.security.api_key import APIKeyHeader
import redis.asyncio as redis
from redis.commands.json.path import Path

from src import function, schema

router = APIRouter(prefix="/folder", tags=["folder"], default_response_class=responses.UJSONResponse)

folder_password = APIKeyHeader(name="X-F_Passwd", auto_error=False)
folder_admin_password = APIKeyHeader(name="X-A_Passwd", auto_error=False)


@router.post("/make")
async def folder_make(body: schema.FolderMake):
    DB = await redis.Redis(connection_pool=function.pool(function.FOLDER_DB))

    folder_uuid = str(uuid.uuid4())
    key = hashlib.md5(body.folder_name.encode() + folder_uuid.encode()).hexdigest()
    folder_name = base64.b85encode(body.folder_name.encode()).hex()

    if body.folder_password is None:
        DB_SALT = await redis.Redis(connection_pool=function.pool(function.SALT_DB))

        folder_password_hash = None

        folder_admin_key_salt, folder_admin_key_hash = function.Security(body.folder_admin_password,
                                                                         to_hex=True).hash_new_password()

        await DB_SALT.json().set(folder_uuid.encode().hex(), Path.root_path(),
                                 {"folder_password_salt": None,
                                  "folder_admin_key_salt": folder_admin_key_salt})
        await DB_SALT.close()
    else:
        DB_SALT = await redis.Redis(connection_pool=function.pool(function.SALT_DB))

        folder_password_salt, folder_password_hash = function.Security(body.folder_password,
                                                                       to_hex=True).hash_new_password()
        folder_admin_key_salt, folder_admin_key_hash = function.Security(body.folder_admin_password,
                                                                         to_hex=True).hash_new_password()

        await DB_SALT.json().set(folder_uuid.encode().hex(), Path.root_path(),
                                 {"folder_password_salt": folder_password_salt,
                                  "folder_admin_key_salt": folder_admin_key_salt})
        await DB_SALT.close()

    await DB.set(key, ujson.dumps({
        "folder_uuid": folder_uuid.encode().hex(),
        "folder_name": folder_name,
        "folder_password": folder_password_hash,
        "folder_admin_password": folder_admin_key_hash,
        "folder_contents": []
    }))
    await DB.close()

    return {"folder_id": key, "folder_name": body.folder_name, "folder_url": f"{function.SERVER_URL}/v2/folder/{key}"}


@router.get("/{folder_id}")
async def folder_open(folder_id: str):
    DB = await redis.Redis(connection_pool=function.pool(function.FOLDER_DB))
    json_value = ujson.loads(await DB.get(folder_id))
    await DB.close()

    return json_value


@router.post("/{folder_id}/upload")
async def folder_upload(folder_id: str, files: List[UploadFile] = File(),
                        folder_password: Union[str, None] = Security(folder_password),
                        folder_admin_password: Union[str, None] = Security(folder_admin_password)):
    DB = await redis.Redis(connection_pool=function.pool(function.FOLDER_DB))
    json_value = ujson.loads(await DB.get(folder_id))

    for file in files:
        file_uuid = str(uuid.uuid4())
        file_name = base64.b64encode(bytes(file.filename, 'utf-8')).hex()
        file_size = file.size

        json_value['folder_contents'].append({"file_uuid": file_uuid, "file_name": file_name, "file_size": file_size})

        async with aiofiles.open(f"{function.FOLDER_PATH}/{file_uuid}", "wb") as f:
            for chunk in iter(lambda: file.file.read(1024), b""):
                await f.write(chunk)
        await f.close()

    await DB.set(folder_id, ujson.dumps(json_value))
    await DB.close()

    return {"asdasd": 123}


@router.get("/{folder_id}/{file_uuid}")
async def folder_download(folder_id: str, file_uuid: str):
    file_name: str = ""

    DB = await redis.Redis(connection_pool=function.pool(function.FOLDER_DB))
    json_value = ujson.loads(await DB.get(folder_id))

    file_list: list = json_value['folder_contents']

    for file_list_data in file_list:
        if file_list_data['file_uuid'] is file_uuid:
            file_name = file_list_data['file_name']

    if file_name is "":
        return HTTPException(404, "파일이 존제하지 않습니다!")

    return fastapi.responses.FileResponse(f"{function.FOLDER_PATH}/{file_uuid}", filename=file_name)
