import os
import uuid

import aiofiles
from fastapi import *
from fastapi import Security, HTTPException
from fastapi.responses import *
from fastapi.security.api_key import APIKeyHeader
from redis.asyncio import Redis

from main import *
from src.function import *

router = APIRouter(prefix="/file", tags=["file"])

password_header = APIKeyHeader(name="x-password", auto_error=False)


# noinspection PyUnresolvedReferences,PyShadowingNames
@router.get("/download/{file_id}")
async def file_download(
    request: Request,
    file_id: str,
    file: Union[str, None] = None,
    password: Union[str, None] = Security(password_header),
):
    """
    Handles the file download endpoint to serve files securely, with additional
    provisions for password protection and support for HTTP Range requests.

    :param request: The request object representing the client's HTTP request.
                    Used to extract headers and metadata necessary for file
                    streaming or download verification.
    :type request: Request

    :param file_id: Unique identifier for the requested file to be served.
                    This ID is used to locate or fetch the file metadata from
                    the Redis database.
    :type file_id: str

    :param file: Optional name of the file provided by the client.
                 Used for setting the filename in the response for direct
                 downloads when the `Range` header is not specified.
    :type file: Union[str, None]

    :param password: Password for file access, extracted securely via the
                     password_header dependency. If the file is password-
                     protected, this parameter is validated against the stored
                     version.
    :type password: Union[str, None]

    :return: A StreamingResponse or FileResponse object if the file download
             is successful or matches the requested range. May also return
             an HTMLResponse with an error message in case of missing or
             incorrect credentials.
    :rtype: Union[Response, FileResponse, HTMLResponse, HTTPException]
    """
    try:
        redis_file_db_password = redis.Redis(connection_pool=pool(PASSWORD_DB))
        password_db = await redis_file_db_password.get(file_id)
        password_db = password_db.decode("utf-8")
        await redis_file_db_password.close()
        password_db = bytes.fromhex(password_db).decode("utf-8")
        password_db = base64.b64decode(password_db).decode("utf-8")

        if password is None:
            return HTMLResponse("Need Password", status_code=403)
        elif password == password_db:
            pass
        else:
            return HTMLResponse("Wrong Password", status_code=403)
    except AttributeError:
        pass

    if file is None:
        redis_file_db_name: Redis = redis.Redis(connection_pool=pool(FILE_DB))
        file_name = await redis_file_db_name.get(file_id)
        file_name = file_name.decode("utf-8")
        await redis_file_db_name.close()
        file_name = bytes.fromhex(file_name).decode("utf-8")
        file_name = base64.b64decode(file_name).decode("utf-8")

        return FileResponse(f"{FILE_PATH}/{file_id}", filename=file_name)
    else:
        range_header = request.headers.get("Range")
        if range_header:
            range_start, range_end = range_header.replace("bytes=", "").split("-")
            range_start = int(range_start)
            range_end = int(range_end) if range_end else None
            file_path = f"{FILE_PATH}/{file_id}"
            file_size = os.path.getsize(file_path)

            if range_start >= file_size:
                raise HTTPException(
                    status_code=416, detail="Requested range not satisfiable"
                )

            if range_end is None or range_end >= file_size:
                range_end = file_size - 1

            content_length = range_end - range_start + 1

            headers = {
                "Content-Range": f"bytes {range_start}-{range_end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(content_length),
            }

            async with aiofiles.open(file_path, "rb") as f:
                await f.seek(range_start)
                data = await f.read(content_length)

            return Response(
                data,
                status_code=206,
                headers=headers,
                media_type="application/octet-stream",
            )
        else:
            return FileResponse(f"{FILE_PATH}/{file_id}", filename=file)


# noinspection PyShadowingNames,PyUnboundLocalVariable
@router.post("/upload")
async def file_upload(
    files: List[UploadFile] = File(),
    password: Union[str, None] = Security(password_header),
) -> ORJSONResponse:
    """
    Handles the upload of files and stores related metadata. This function allows users to upload multiple
    files asynchronously, and optionally secures the files with a password. For every file, metadata such as
    unique identifier (UUID), size, encoded file name, and downloadable URLs are generated and returned in
    the response. The files and their corresponding metadata are saved to the file system and a Redis
    database. If a password is provided, it is also stored securely in a Redis database after encoding.

    :param files: The list of files to upload. Each file should be of type UploadFile.
    :type files: List[UploadFile]
    :param password: Optional security password to protect the files. Defaults to None.
    :type password: Union[str, None]
    :return: An ORJSONResponse containing the status and metadata for the uploaded files. The JSON
    includes fields: password status, file sizes, file UUIDs, file names, direct download URLs,
    and encoded URLs for each uploaded file.
    :rtype: ORJSONResponse
    """
    file_size_list = list()
    file_uuid_list = list()
    file_name_list = list()
    file_url_list = list()
    file_direct_list = list()

    for file in files:
        file_uuid = str(uuid.uuid4())
        file_name = base64.b64encode(bytes(file.filename, "utf-8")).hex()

        file_size_list.append(file.size)
        file_uuid_list.append(file_uuid)
        file_name_list.append(file.filename)
        file_url_list.append(f"{SERVER_URL}/v1/file/download/{file_uuid}")
        file_direct_list.append(
            f"{SERVER_URL}/v1/file/download/{file_uuid}/?file={file.filename}"
        )

        if password is None:
            password_status = "No"
        else:
            password_status = "Yes"
            password = base64.b64encode(bytes(password, "utf-8")).hex()

            redis_file_db_password = redis.Redis(connection_pool=pool(PASSWORD_DB))
            await redis_file_db_password.set(file_uuid, password)
            await redis_file_db_password.close()

        redis_file_db_name = redis.Redis(connection_pool=pool(FILE_DB))
        await redis_file_db_name.set(file_uuid, file_name)
        await redis_file_db_name.close()

        async with aiofiles.open(f"{FILE_PATH}/{file_uuid}", "wb") as file_save:
            while chunk := await file.read(
                1024 * 1024 * 2
            ):  # 2MB 청크 단위로 파일 읽기
                await file_save.write(chunk)

        await file_save.close()
        await file.close()

    return ORJSONResponse(
        content={
            "password": password_status,
            "file_size": file_size_list,
            "file_uuid": file_uuid_list,
            "file_name": file_name_list,
            "file_url": file_url_list,
            "file_direct": file_direct_list,
        },
        status_code=200,
    )
