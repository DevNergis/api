#Qloat APK Archive

from main import *
from src.function import *
from src.schema import *

router = APIRouter(prefix="/api/v1/qloat", tags=["qloat"])

@router.get("/archive/download/{file_id}")
async def file_download(file_id: str, file: Union[str, None] = None, password: Union[str, None] = "password"):
    redis_file_db_password = redis.StrictRedis(host='localhost', port=6379, db=1)
    password_db = redis_file_db_password.get(file_id).decode('utf-8')
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
        redis_file_db_name = redis.StrictRedis(host='localhost', port=6379, db=0)
        file_name = redis_file_db_name.get(file_id).decode('utf-8')
        file_name = bytes.fromhex(file_name).decode('utf-8')
        file_name = base64.b64decode(file_name).decode("utf-8")
        redis_file_db_name.close()

        return FileResponse(f"{FILE_PATH}/{file_id}", filename=file_name)
    else:
        return FileResponse(f"{FILE_PATH}/{file_id}", filename=file)

@router.post("/archive/upload")
async def file_upload(body: qloat_body_, files: List[UploadFile] = File()):
    file_size_list = list()
    file_uuid_list = list()
    file_name_list = list()
    file_url_list = list()
    file_direct_list = list()
    file_name_str = f"Qloat-{DATE_QLOAT}.apk"
    password = body.password

    for file in files:
        file_uuid = str(uuid.uuid4())
        file_name = base64.b64encode(bytes(file_name_str, 'utf-8')).hex()

        if password == QLOAT_PASSWORD:
            password = base64.b64encode(bytes(password, 'utf-8')).hex()

            redis_file_db_password = redis.StrictRedis(host='localhost', port=6379, db=1)
            redis_file_db_password.set(file_uuid, password)
            redis_file_db_password.close()
        else:
            return ORJSONResponse(content={"fu": "ck"})

        redis_file_db_name = redis.StrictRedis(host='localhost', port=6379, db=0)
        redis_file_db_name.set(file_uuid, file_name)
        redis_file_db_name.close()

        with open(f"{FILE_PATH_QLOAT}/{file_uuid}", "wb") as file_save:
            file_save.write(file.file.read(20*1024*1024))

        file.file.close()

        file_size_list.append(file.size)
        file_uuid_list.append(file_uuid)
        file_name_list.append(file_name_str)
        file_url_list.append(f"{SERVER_URL}/file/download/{file_uuid}")
        file_direct_list.append(f"{SERVER_URL}/file/download/{file_uuid}/?file={file_name_str}")

    return ORJSONResponse(content={"file_size": file_size_list, "file_uuid": file_uuid_list, "file_name": file_name_list, "file_url": file_url_list, "file_direct": file_direct_list}, status_code=200)
#end
