from typing import *
import random, orjson
from datetime import *
from mojang import API as MojangAPI
from fastapi import *
from fastapi.responses import *
from yt_dlp import YoutubeDL
from pydantic import BaseModel
from io import BytesIO
import redis, base64, dotenv, requests, uuid

app = FastAPI(title="FDZZ API", description="FDZZ API", version="5.0.0", default_response_class=ORJSONResponse)

# 공용
FILE_PATH = dotenv.get_key(".env", "FILE_PATH")
OPEN_NEIS_API_KEY = dotenv.get_key(".env", "OPEN_NEIS_API_KEY")
YDL_OPTIONS = dotenv.get_key(".env", "YDL_OPTIONS")
HEADERS = dotenv.get_key(".env", "HEADERS")
SERVER_URL = dotenv.get_key(".env", "SERVER_URL")
DATE = datetime.now().strftime('%Y%m%d')
def YDL_URL(url):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)

    URL = info['formats'][0]['url']
    return URL
def YDL_cache(URL: str, NAME: str):
    with requests.get(URL, stream=True, headers=HEADERS) as file_request:
        content = BytesIO()
        
        for chunk in file_request.iter_content(chunk_size=1*1024*1024):
            content.write(chunk)

        with open(f"{NAME}", "wb") as file_save:
            file_save.write(content.getbuffer())
        
        content.seek(0)

    return URL, NAME
# END


@app.get("/")
async def main():
    return FileResponse("src/index.html")

@app.get("/style.css")
async def main_sytle():
    return FileResponse("src/style.css")

@app.post('/my-endpoint')
async def my_endpoint(request: Request):
    ip = request.client.host
    return ORJSONResponse(content={"ip":f"{ip}"}, status_code=200)

class _cdt(BaseModel):
    server_name: str
    invite_link: str
    random: bool

class mealServiceDietInfo_(BaseModel):
    SchoolName: str
@app.post("/api/school/meal")
async def mealServiceDietInfo(body: mealServiceDietInfo_):
    url = f"https://open.neis.go.kr/hub/schoolInfo?KEY={OPEN_NEIS_API_KEY}&Type=json&pIndex=1&pSize=10&SCHUL_NM={body.SchoolName}"
    request = requests.get(url=url, headers=HEADERS)
    r = orjson.loads(request.text)
    rr = r['schoolInfo'][-1]
    rrr = rr['row'][-1]
    ATPT_OFCDC_SC_CODE = rrr['ATPT_OFCDC_SC_CODE']
    SD_SCHUL_CODE = rrr['SD_SCHUL_CODE']
    url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?KEY={OPEN_NEIS_API_KEY}&Type=json&pIndex=1&pSize=10&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}&SD_SCHUL_CODE={SD_SCHUL_CODE}&MLSV_YMD={DATE}"
    request = requests.get(url=url, headers=HEADERS)
    if request.text == """{"RESULT":{"CODE":"INFO-200","MESSAGE":"해당하는 데이터가 없습니다."}}""":
        return ORJSONResponse(content={"RESULT":{"CODE":"INFO-200","MESSAGE":"해당하는 데이터가 없습니다."}}, status_code=200)
    else:
        r = orjson.loads(request.text)
        rr = r['mealServiceDietInfo'][-1]
        rrr = rr['row'][-1]
        DDISH_NM = rrr['DDISH_NM']
        DDISH_NM_LIST = DDISH_NM.replace('<br/>', '\n')
        return ORJSONResponse(content={"SchoolName":f"{body.SchoolName}", "SchoolMeal":[DDISH_NM_LIST]}, status_code=200)

@app.get("/api/img/sfw")
async def api_img():
    import requests
    optional = random.choice(["waifu","neko","shinobu","megumin","bully","cuddle","cry","hug","awoo","kiss","lick","pat","smug","bonk","yeet","blush","smile","wave","highfive","handhold","nom","bite","glomp","slap","kill","kick","happy","wink","poke","dance","cringe"])
    sfw = requests.get(f"https://api.waifu.pics/sfw/{optional}")
    if (sfw.status_code == requests.codes.ok):
        sfw = sfw.json()
        sfw = sfw["url"]
        print(sfw)
        return ORJSONResponse(content={"url":f"{sfw}"}, status_code=200)

@app.get("/yt-dla")
async def youtube_dl(url: str):
    URL = YDL_URL(url)

    return HTMLResponse(content=f"""{URL}""", status_code=200)

@app.get("/minecraft/info")
async def minecraft(name: str):
    uuid = MojangAPI.get_uuid(name)

    if not uuid:
        return ORJSONResponse(content={"error":f"{name} is not a taken username."})
    else:
        profile = MojangAPI.get_profile(uuid)
        return ORJSONResponse(content={"name":f"{name}", "uuid":f"{uuid}", "skin":f"{profile.skin_url}", "model":f"{profile.skin_model}", "cape":f"{profile.cape_url}"}, status_code=200)

@app.get("/minecraft/render")
async def skinrender(name: str):
    return HTMLResponse(content=
    """
    <!DOCTYPE html>
    <html>

        <head>
            <title>%s Skin Render</title>
            <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/jquery.min.js" integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8=" crossorigin="anonymous"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/94/three.min.js" integrity="sha256-NGC9JEuTWN4GhTj091wctgjzftr+8WNDmw0H8J5YPYE=" crossorigin="anonymous"></script>
            <script src="https://cdn.jsdelivr.net/gh/InventivetalentDev/MineRender@1.4.6/dist/skin.min.js"></script>
        </head>

        <body>
            <script>
                var skinRender = new SkinRender({/* options */}, document.getElementById("mySkinContainer"));
                skinRender.render("%s");
            </script>
        </body>

    </html>
    """ % (name, name), status_code=200)

#file api
@app.get("/file/direct/{file_name}")
async def file_direct(file_name: str):
    file= base64.b64encode(bytes(file_name, 'utf-8'))

    return FileResponse(f"{FILE_PATH}/{file}", filename=file_name)

@app.get("/file/download/")
async def file_downlload_html():
    return FileResponse("src/download.html")

@app.get("/file/download/{file_id}")
async def file_download(file_id: str):
    rd = redis.StrictRedis(host='localhost', port=6379, db=0)

    file = rd.get(file_id).decode('utf-8')
    file_name = bytes.fromhex(file).decode('utf-8')
    file_name = base64.b64decode(file_name).decode("utf-8")

    return FileResponse(f"{FILE_PATH}/{file}", filename=file_name)

@app.post("/file/upload/")
async def file_upload(files: List[UploadFile] = File()):
    file_size_list = list()
    file_uuid_list = list()
    file_name_list = list()
    file_url_list = list()

    for file in files:

        file_uuid = str(uuid.uuid4())
        file_name = base64.b64encode(bytes(file.filename, 'utf-8')).hex()

        rd = redis.StrictRedis(host='localhost', port=6379, db=0)
        rd.set(file_uuid, file_name)

        with open(f"{FILE_PATH}/{file_name}", "wb") as file_save:
            file_save.write(file.file.read(20*1024*1024))

        file.file.close()

        file_size_list.append(file.size)
        file_uuid_list.append(file_uuid)
        file_name_list.append(file.filename)
        file_url_list.append(f"{SERVER_URL}/file/download/{file_uuid}")

    return ORJSONResponse(content={"file_size": file_size_list, "file_uuid": file_uuid_list, "file_name": file_name_list, "file_url": file_url_list}, status_code=200)
