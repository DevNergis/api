import base64
import uuid
import os
from math import ceil

from aioredis import Redis

from main import *
from src.function import *
import aiofiles
from fastapi.security.api_key import APIKeyHeader
from fastapi import Security, Request, HTTPException

router = APIRouter(prefix="/file", tags=["file"])

password_header = APIKeyHeader(name="x-password", auto_error=False)


# noinspection PyUnresolvedReferences,PyShadowingNames
@router.get("/download/{file_id}")
async def file_download(request: Request, file_id: str, file: Union[str, None] = None,
                        password: Union[str, None] = Security(password_header)):
    try:
        redis_file_db_password = redis.Redis(connection_pool=pool(PASSWORD_DB))
        password_db = await redis_file_db_password.get(file_id)
        password_db = password_db.decode('utf-8')
        await redis_file_db_password.close()
        password_db = bytes.fromhex(password_db).decode('utf-8')
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
        file_name = file_name.decode('utf-8')
        await redis_file_db_name.close()
        file_name = bytes.fromhex(file_name).decode('utf-8')
        file_name = base64.b64decode(file_name).decode("utf-8")

        return FileResponse(f"{FILE_PATH}/{file_id}", filename=file_name)
    else:

        file_path = f"{FILE_PATH}/{file_id}"
        file_size = os.path.getsize(file_path)

        range_header = request.headers.get('Range', None)
        if range_header:
            bytes_range = range_header.removeprefix("bytes=").split("-")
            if bytes_range[0] == '':
                start = 0
            else:
                start = int(bytes_range[0])
            if len(bytes_range) < 2 or bytes_range[1] == '':
                end = file_size
            else:
                end = int(bytes_range[1])
        else:
            start, end = 0, file_size

        if start >= file_size:
            return HTTPException(status_code=416, detail="Range not satisfiable")

        content_length = end - start
        headers = {
            "Content-Disposition": f"attachment;filename={file}",
            "Content-Type": "application/octet-stream",
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Content-Length": str(content_length),
            "Accept-Ranges": "bytes",
        }

        def content():
            with open(file_path, 'rb') as file_1:
                file_1.seek(start)
                while True:
                    data = file_1.read(1024)
                    if not data:
                        break
                    yield data

        return StreamingResponse(content(), headers=headers, media_type="application/octet-stream")




        #return FileResponse(f"{FILE_PATH}/{file_id}", filename=file)


# noinspection PyShadowingNames,PyUnboundLocalVariable
@router.post("/upload")
async def file_upload(files: List[UploadFile] = File(), password: Union[str, None] = Security(password_header)):
    file_size_list = list()
    file_uuid_list = list()
    file_name_list = list()
    file_url_list = list()
    file_direct_list = list()

    for file in files:
        file_uuid = str(uuid.uuid4())
        file_name = base64.b64encode(bytes(file.filename, 'utf-8')).hex()

        file_size_list.append(file.size)
        file_uuid_list.append(file_uuid)
        file_name_list.append(file.filename)
        file_url_list.append(f"{SERVER_URL}/v1/file/download/{file_uuid}")
        file_direct_list.append(f"{SERVER_URL}/v1/file/download/{file_uuid}/?file={file.filename}")

        if password is None:
            password_status = "No"
        else:
            password_status = "Yes"
            password = base64.b64encode(bytes(password, 'utf-8')).hex()

            redis_file_db_password = redis.Redis(connection_pool=pool(PASSWORD_DB))
            await redis_file_db_password.set(file_uuid, password)
            await redis_file_db_password.close()

        redis_file_db_name = redis.Redis(connection_pool=pool(FILE_DB))
        await redis_file_db_name.set(file_uuid, file_name)
        await redis_file_db_name.close()

        chunk = BytesIO()
        chunk_range = range(ceil(file.size / (1024 * 1024 * 2)))

        for _ in chunk_range:
            chunk.write(await file.read(1024 * 1024 * 2))

        chunk.seek(0)

        async with aiofiles.open(f"{FILE_PATH}/{file_uuid}", "wb") as file_save:
            await file_save.write(chunk.read())

        chunk.close()
        file.file.close()
        await file.close()

    return ORJSONResponse(
        content={"password": password_status, "file_size": file_size_list, "file_uuid": file_uuid_list,
                 "file_name": file_name_list, "file_url": file_url_list, "file_direct": file_direct_list},
        status_code=200)
