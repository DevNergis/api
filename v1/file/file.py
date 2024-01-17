from math import ceil
from main import *
from src.function import *
from src.schema import *
import aiofiles

router = APIRouter(prefix="/v1/file", tags=["file"])

@router.get("/download/{file_id}")
async def file_download(file_id: str, file: Union[str, None] = None, password: Union[str, None] = "password"):
    redis_file_db_password = redis.Redis(connection_pool=pool(PASSWORD_DB))
    password_db = redis_file_db_password.get(file_id).decode('utf-8')
    redis_file_db_password.close()
    password_db = bytes.fromhex(password_db).decode('utf-8')
    password_db = base64.b64decode(password_db).decode("utf-8")

    if password == "password":
        if password == password_db:
            pass
        else:
            return HTMLResponse("Need Password", status_code=403)
    else:
        if password == password_db:
            pass
        else:
            if password_db == "password":
                return HTMLResponse("No Password Required", status_code=403)
            else:
                return HTMLResponse("Wrong Password", status_code=403)

    if file == None:
        redis_file_db_name = redis.Redis(connection_pool=pool(FILE_DB))
        file_name = redis_file_db_name.get(file_id).decode('utf-8')
        redis_file_db_name.close()
        file_name = bytes.fromhex(file_name).decode('utf-8')
        file_name = base64.b64decode(file_name).decode("utf-8")

        return FileResponse(f"{FILE_PATH}/{file_id}", filename=file_name)
    else:
        return FileResponse(f"{FILE_PATH}/{file_id}", filename=file)

@router.post("/upload")
async def file_upload(files: List[UploadFile] = File(), password: Union[str, None] = None):
    file_size_list = list()
    file_uuid_list = list()
    file_name_list = list()
    file_url_list = list()
    file_direct_list = list()

    for file in files:
        file_uuid = str(uuid.uuid4())
        file_name = base64.b64encode(bytes(file.filename, 'utf-8')).hex()

        if password != None:
            password = base64.b64encode(bytes(password, 'utf-8')).hex()

            redis_file_db_password = redis.Redis(connection_pool=pool(PASSWORD_DB))
            redis_file_db_password.set(file_uuid, password)
            redis_file_db_password.close()
        else:
            password = base64.b64encode(bytes("password", 'utf-8')).hex()

            redis_file_db_password = redis.Redis(connection_pool=pool(PASSWORD_DB))
            redis_file_db_password.set(file_uuid, password)
            redis_file_db_password.close()

        redis_file_db_name = redis.Redis(connection_pool=pool(FILE_DB))
        redis_file_db_name.set(file_uuid, file_name)
        redis_file_db_name.close()

        chunk = BytesIO()
        chunk_range = range(ceil(file.size / (1024*1024*2)))
        
        for _ in chunk_range:
            chunk.write(await file.read(1024*1024*2))

        chunk.seek(0)

        async with aiofiles.open(f"{FILE_PATH}/{file_uuid}", "wb") as file_save:
            await file_save.write(chunk.read())

        chunk.close()
        file.file.close()
        file.close()

        file_size_list.append(file.size)
        file_uuid_list.append(file_uuid)
        file_name_list.append(file.filename)
        file_url_list.append(f"{SERVER_URL}/file/download/{file_uuid}")
        file_direct_list.append(f"{SERVER_URL}/file/download/{file_uuid}/?file={file.filename}")
        if password == "password":
            password_status = "No"
        else:
            password_status = "Yes"

    return ORJSONResponse(content={"password": password_status, "file_size": file_size_list, "file_uuid": file_uuid_list, "file_name": file_name_list, "file_url": file_url_list, "file_direct": file_direct_list}, status_code=200)
