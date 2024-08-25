import hashlib
import uuid
import aiofiles
import fastapi.responses
from typing import *
from fastapi import *
from redis.commands.json.path import Path
from src import function
from src import schema
import redis.asyncio as aioredis


router = APIRouter(prefix="/folder", tags=["folder"], default_response_class=responses.ORJSONResponse)

folder_password = fastapi.Header(default=None)
folder_admin_password = fastapi.Header(default=None)


@router.post("/make")
async def folder_make(body: schema.FolderMake):
    DB = await aioredis.Redis(connection_pool=function.pool(function.FOLDER_DB))

    folder_uuid = function.Obfuscation(str(uuid.uuid4())).on()
    key = hashlib.md5(body.folder_name.encode() + folder_uuid.encode()).hexdigest()
    folder_name = function.Obfuscation(body.folder_name).on()

    if body.folder_password is None:
        DB_SALT = aioredis.Redis(connection_pool=function.pool(function.SALT_DB))

        folder_password_hash = None

        folder_admin_key_salt, folder_admin_key_hash = function.Security(body.folder_admin_password,
                                                                         to_hex=True).hash_new_password()

        await DB_SALT.json().set(folder_uuid, Path.root_path(),
                                 {"folder_password_salt": None,
                                  "folder_admin_key_salt": folder_admin_key_salt})
        await DB_SALT.close()
    else:
        DB_SALT = aioredis.Redis(connection_pool=function.pool(function.SALT_DB))

        folder_password_salt, folder_password_hash = function.Security(body.folder_password,
                                                                       to_hex=True).hash_new_password()
        folder_admin_key_salt, folder_admin_key_hash = function.Security(body.folder_admin_password,
                                                                         to_hex=True).hash_new_password()

        await DB_SALT.json().set(folder_uuid, Path.root_path(),
                                 {"folder_password_salt": folder_password_salt,
                                  "folder_admin_key_salt": folder_admin_key_salt})
        await DB_SALT.close()

    await DB.set(key, await function.aiorjson.dumps({
        "folder_uuid": folder_uuid,
        "folder_name": folder_name,
        "folder_password": folder_password_hash,
        "folder_admin_password": folder_admin_key_hash,
        "folder_contents": []
    }))
    await DB.close()

    return {"folder_id": key, "folder_name": body.folder_name, "folder_url": f"{function.SERVER_URL}/v2/folder/{key}"}


@router.get("/{folder_id}")
async def folder_open(folder_id: str, X_F_Passwd: Optional[str] = folder_password):
    DB = aioredis.Redis(connection_pool=function.pool(function.FOLDER_DB))
    DB_SALT = aioredis.Redis(connection_pool=function.pool(function.SALT_DB))

    json_value = await function.aiorjson.loads(await DB.get(folder_id))
    salt_json_value = await DB_SALT.json().get(json_value['folder_uuid'])

    await DB.close()
    await DB_SALT.close()

    file_list: list = json_value['folder_contents']

    try:
        folder_key_hash = function.Obfuscation(json_value['folder_password']).hexoff()
        folder_key_salt = function.Obfuscation(salt_json_value['folder_password_salt']).hexoff()
    except TypeError:
        return {"folder_contents": file_list}
    
    if function.Security(X_F_Passwd, folder_key_salt, folder_key_hash).is_correct_password():
        return {"folder_contents": file_list}
    else:
        return HTTPException(status.HTTP_401_UNAUTHORIZED, detail="비번 틀림")


# noinspection PyPep8Naming,DuplicatedCode
@router.post("/{folder_id}/upload")
async def folder_upload(folder_id: str, files: List[UploadFile] = File(),
                        X_A_Passwd: str = folder_admin_password):
    file_uuid_list: list = []

    DB = aioredis.Redis(connection_pool=function.pool(function.FOLDER_DB))
    DB_SALT = aioredis.Redis(connection_pool=function.pool(function.SALT_DB))

    json_value = await function.aiorjson.loads(await DB.get(folder_id))
    salt_json_value = await DB_SALT.json().get(json_value['folder_uuid'])

    await DB.close()
    await DB_SALT.close()

    folder_admin_key_hash = function.Obfuscation(json_value['folder_admin_password']).hexoff()
    folder_admin_key_salt = function.Obfuscation(salt_json_value['folder_admin_key_salt']).hexoff()

    try:
        if function.Security(X_A_Passwd, folder_admin_key_salt, folder_admin_key_hash).is_correct_password():
            for file in files:
                __uuid__ = str(uuid.uuid4())

                file_uuid_list.append(__uuid__)

                file_uuid = function.Obfuscation(__uuid__).on()
                file_name = function.Obfuscation(file.filename).on()
                file_size = file.size

                json_value['folder_contents'].append(
                    {"file_uuid": file_uuid, "file_name": file_name, "file_size": file_size})

                async with aiofiles.open(f"{function.FOLDER_PATH}/{file_uuid}", "wb") as f:
                    while chunk := await file.read(1024 * 1024 * 2):  # 2MB 청크 단위로 파일 읽기
                        await f.write(chunk)
                await f.close()
                await file.close()

            await DB.set(folder_id, await function.aiorjson.dumps(json_value))

            return {"file_uuid": file_uuid_list}
        else:
            return HTTPException(status.HTTP_401_UNAUTHORIZED, detail="비번 틀림")
    except AttributeError:
        return HTTPException(status.HTTP_401_UNAUTHORIZED, detail="비번 틀림")


# noinspection DuplicatedCode,PyPep8Naming
@router.get("/{folder_id}/{file_uuid}")
async def folder_download(folder_id: str, file_uuid: str, X_F_Passwd: Optional[str] = folder_password):
    file_name: str = ""
    file_list_data: dict = {}

    DB = aioredis.Redis(connection_pool=function.pool(function.FOLDER_DB))
    DB_SALT = aioredis.Redis(connection_pool=function.pool(function.SALT_DB))

    json_value = await function.aiorjson.loads(await DB.get(folder_id))
    salt_json_value = await DB_SALT.json().get(json_value['folder_uuid'])

    await DB.close()
    await DB_SALT.close()

    file_list: list = json_value['folder_contents']

    try:
        folder_key_hash = function.Obfuscation(json_value['folder_password']).hexoff()
        folder_key_salt = function.Obfuscation(salt_json_value['folder_password_salt']).hexoff()
    except TypeError:
        for file_list_data in file_list:
                if function.Obfuscation(file_list_data['file_uuid']).off() == file_uuid:
                    file_name = function.Obfuscation(file_list_data['file_name']).off()

        if file_name == "":
            return HTTPException(404, "파일이 존제하지 않습니다!")

        return fastapi.responses.FileResponse(f"{function.FOLDER_PATH}/{file_list_data['file_uuid']}", filename=file_name)

    try:
        if function.Security(X_F_Passwd, folder_key_salt, folder_key_hash).is_correct_password():
            for file_list_data in file_list:
                if function.Obfuscation(file_list_data['file_uuid']).off() == file_uuid:
                    file_name = function.Obfuscation(file_list_data['file_name']).off()

            if file_name == "":
                return HTTPException(404, "파일이 존제하지 않습니다!")

            return fastapi.responses.FileResponse(f"{function.FOLDER_PATH}/{file_list_data['file_uuid']}", filename=file_name)
        else:
            return HTTPException(status.HTTP_401_UNAUTHORIZED, detail="비번 틀림")
    except AttributeError:
        return HTTPException(status.HTTP_401_UNAUTHORIZED, detail="비번 틀림")
