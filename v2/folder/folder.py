"""Folder v2"""

import hashlib
import uuid
from typing import List, Optional, Union
import aiofiles
import redis.asyncio as aioredis
from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
    status,
    responses,
    Header,
)
from redis.commands.json.path import Path

from src import function, schema

router = APIRouter(
    prefix="/folder", tags=["folder"], default_response_class=responses.ORJSONResponse
)

folder_password = Header(default=None)
folder_admin_password = Header(default=None)


@router.post("/make")
async def folder_make(body: schema.FolderMake):
    """
    Creates a new folder with the provided parameters such as folder name, folder
    password, and admin password, generates a unique ID and obfuscates data using
    custom utilities. The folder metadata and credentials are securely stored in
    different Redis databases, ensuring proper separation and security.

    If no folder password is provided, only the admin password is hashed and stored.
    Otherwise, both the folder and admin passwords are hashed and saved into a Redis
    database for later access and authentication.

    :param body: Contains the parameters required to create a folder, including its
        name, optionally a folder password, and an admin password.
        - folder_name: str
        - folder_password: Optional[str]
        - folder_admin_password: str
    :return: A dictionary containing details about the created folder, including:
        - folder_id: The hashed key representing the folder ID.
        - folder_name: The original folder name provided in the input.
        - folder_url: The URL referencing the newly created folder.
    """
    db = await aioredis.Redis(connection_pool=function.pool(function.FOLDER_DB))

    folder_uuid = function.Obfuscation(str(uuid.uuid4())).on()
    key = hashlib.md5(body.folder_name.encode() + folder_uuid.encode()).hexdigest()
    folder_name = function.Obfuscation(body.folder_name).on()

    if body.folder_password is None:
        db_salt = aioredis.Redis(connection_pool=function.pool(function.SALT_DB))

        folder_password_hash = None

        folder_admin_key_salt, folder_admin_key_hash = function.HashingUtility(
            body.folder_admin_password, to_hex=True
        ).hash_new_password()

        await db_salt.json().set(
            folder_uuid,
            Path.root_path(),
            {
                "folder_password_salt": None,
                "folder_admin_key_salt": folder_admin_key_salt,
            },
        )
        await db_salt.close()
    else:
        db_salt = aioredis.Redis(connection_pool=function.pool(function.SALT_DB))

        folder_password_salt, folder_password_hash = function.HashingUtility(
            body.folder_password, to_hex=True
        ).hash_new_password()
        folder_admin_key_salt, folder_admin_key_hash = function.HashingUtility(
            body.folder_admin_password, to_hex=True
        ).hash_new_password()

        await db_salt.json().set(
            folder_uuid,
            Path.root_path(),
            {
                "folder_password_salt": folder_password_salt,
                "folder_admin_key_salt": folder_admin_key_salt,
            },
        )
        await db_salt.close()

    await db.set(
        key,
        await function.aiorjson.dumps(
            {
                "folder_uuid": folder_uuid,
                "folder_name": folder_name,
                "folder_password": folder_password_hash,
                "folder_admin_password": folder_admin_key_hash,
                "folder_contents": [],
            }
        ),
    )
    await db.close()

    return {
        "folder_id": key,
        "folder_name": body.folder_name,
        "folder_url": f"{function.SERVER_URL}/v2/folder/{key}",
    }


@router.get("/{folder_id}")
async def folder_open(folder_id: str, x_f_passwd: Optional[str] = folder_password):
    """
    Handles the retrieval and decryption of folder data using provided password credentials,
    if required, and returns the file list within the specified folder. It interacts with
    Redis databases to perform folder data and associated salt retrievals and leverages
    custom obfuscation and hashing utilities for security operations.

    :param folder_id: The unique identifier of the folder to be accessed.
    :type folder_id: str
    :param x_f_passwd: Optional password provided to unlock the folder's contents, if a password
        is required.
    :type x_f_passwd: Optional[str]
    :return: A dictionary containing a list of contents of the requested folder, each having
        details about the file's UUID, name, and size. In case of an erroneous or incorrect
        password, a 401 Unauthorized HTTP Exception is raised.
    :rtype: dict
    """
    decoded_file_list: list = []

    db = aioredis.Redis(connection_pool=function.pool(function.FOLDER_DB))
    db_salt = aioredis.Redis(connection_pool=function.pool(function.SALT_DB))

    json_value = await function.aiorjson.loads(await db.get(folder_id))
    salt_json_value = await db_salt.json().get(json_value["folder_uuid"])

    await db.close()
    await db_salt.close()

    file_list: list = json_value["folder_contents"]

    try:
        folder_key_hash = function.Obfuscation(json_value["folder_password"]).hexoff()
        folder_key_salt = function.Obfuscation(
            salt_json_value["folder_password_salt"]
        ).hexoff()
    except TypeError:
        for file_data in file_list:
            decoded_file_list.append(
                {
                    "file_uuid": function.Obfuscation(file_data["file_uuid"]).off(),
                    "file_name": function.Obfuscation(file_data["file_name"]).off(),
                    "file_size": file_data["file_size"],
                }
            )

        return {"folder_contents": decoded_file_list}

    try:
        if function.HashingUtility(
            x_f_passwd, folder_key_salt, folder_key_hash
        ).is_correct_password():
            for file_data in file_list:
                decoded_file_list.append(
                    {
                        "file_uuid": function.Obfuscation(file_data["file_uuid"]).off(),
                        "file_name": function.Obfuscation(file_data["file_name"]).off(),
                        "file_size": file_data["file_size"],
                    }
                )

            return {"folder_contents": decoded_file_list}
        else:
            return HTTPException(status.HTTP_401_UNAUTHORIZED, detail="비번 틀림")
    except AttributeError:
        return HTTPException(status.HTTP_401_UNAUTHORIZED, detail="비번 틀림")


# noinspection PyPep8Naming,DuplicatedCode
@router.post("/{folder_id}/upload")
async def folder_upload(
    folder_id: str,
    files: List[UploadFile] = File(),
    X_A_Passwd: str = folder_admin_password,
):
    """
    Handles the upload of files to a specific folder by verifying the folder admin's
    password, storing file metadata in a Redis database, and saving the files in
    the filesystem.

    :param folder_id: Unique identifier for the folder to which the files will be
        uploaded.
    :type folder_id: str
    :param files: List of files to be uploaded.
    :type files: List[UploadFile]
    :param X_A_Passwd: Admin password for the folder, used for authentication.
    :type X_A_Passwd: str
    :return: A dictionary containing the unique identifiers (UUIDs) of the uploaded
        files if the upload is successful.
    :rtype: dict
    :raises HTTPException: * 401 Unauthorized - If the provided admin password is
        incorrect or authentication fails.
    """
    file_uuid_list: list = []

    DB = aioredis.Redis(connection_pool=function.pool(function.FOLDER_DB))
    DB_SALT = aioredis.Redis(connection_pool=function.pool(function.SALT_DB))

    json_value = await function.aiorjson.loads(await DB.get(folder_id))
    salt_json_value = await DB_SALT.json().get(json_value["folder_uuid"])

    await DB.close()
    await DB_SALT.close()

    folder_admin_key_hash = function.Obfuscation(
        json_value["folder_admin_password"]
    ).hexoff()
    folder_admin_key_salt = function.Obfuscation(
        salt_json_value["folder_admin_key_salt"]
    ).hexoff()

    try:
        if function.HashingUtility(
            X_A_Passwd, folder_admin_key_salt, folder_admin_key_hash
        ).is_correct_password():
            for file in files:
                __uuid__ = str(uuid.uuid4())

                file_uuid_list.append(__uuid__)

                file_uuid = function.Obfuscation(__uuid__).on()
                file_name = function.Obfuscation(file.filename).on()
                file_size = file.size

                json_value["folder_contents"].append(
                    {
                        "file_uuid": file_uuid,
                        "file_name": file_name,
                        "file_size": file_size,
                    }
                )

                async with aiofiles.open(
                    f"{function.FOLDER_PATH}/{file_uuid}", "wb"
                ) as f:
                    while chunk := await file.read(
                        1024 * 1024 * 2
                    ):  # 2MB 청크 단위로 파일 읽기
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
async def folder_download(
    folder_id: str, file_uuid: str, X_F_Passwd: Optional[str] = folder_password
) -> Union[responses.FileResponse, HTTPException]:
    """
    Handles the download of files from a folder. This endpoint retrieves folder and file
    information from Redis databases, validates the provided password if required, and
    delivers the requested file.

    :param folder_id: The ID of the folder containing the file
    :type folder_id: str
    :param file_uuid: The unique identifier of the requested file
    :type file_uuid: str
    :param X_F_Passwd: Optional password for accessing the folder, if applicable
    :type X_F_Passwd: Optional[str]
    :return: A response containing the requested file, or an exception if the file is not
             found or if the access is unauthorized due to a password mismatch
    :rtype: Union[responses.FileResponse, HTTPException]
    """
    file_name: str = ""
    file_list_data: dict = {}

    DB = aioredis.Redis(connection_pool=function.pool(function.FOLDER_DB))
    DB_SALT = aioredis.Redis(connection_pool=function.pool(function.SALT_DB))

    json_value = await function.aiorjson.loads(await DB.get(folder_id))
    salt_json_value = await DB_SALT.json().get(json_value["folder_uuid"])

    await DB.close()
    await DB_SALT.close()

    file_list: list = json_value["folder_contents"]

    try:
        folder_key_hash = function.Obfuscation(json_value["folder_password"]).hexoff()
        folder_key_salt = function.Obfuscation(
            salt_json_value["folder_password_salt"]
        ).hexoff()
    except TypeError:
        for file_list_data in file_list:
            if function.Obfuscation(file_list_data["file_uuid"]).off() == file_uuid:
                file_name = function.Obfuscation(file_list_data["file_name"]).off()

        if file_name == "":
            return HTTPException(404, "파일이 존제하지 않습니다!")

        return responses.FileResponse(
            f"{function.FOLDER_PATH}/{file_list_data['file_uuid']}", filename=file_name
        )

    try:
        if function.HashingUtility(
            X_F_Passwd, folder_key_salt, folder_key_hash
        ).is_correct_password():
            for file_list_data in file_list:
                if function.Obfuscation(file_list_data["file_uuid"]).off() == file_uuid:
                    file_name = function.Obfuscation(file_list_data["file_name"]).off()

            if file_name == "":
                return HTTPException(404, "파일이 존제하지 않습니다!")

            return responses.FileResponse(
                f"{function.FOLDER_PATH}/{file_list_data['file_uuid']}",
                filename=file_name,
            )
        else:
            return HTTPException(status.HTTP_401_UNAUTHORIZED, detail="비번 틀림")
    except AttributeError:
        return HTTPException(status.HTTP_401_UNAUTHORIZED, detail="비번 틀림")
