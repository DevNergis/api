from typing import *
import random, orjson
from datetime import *
from mojang import API as MojangAPI
from fastapi import *
from fastapi.responses import *
from src.function import *
from src.schema import *
import base64, requests, uuid, re

from api.v1.qloat import qaa
from api.v1.school import school
from api.v1.img import sfw
from api.v1.file import file

app = FastAPI(debug=True ,title="FDZZ API", description="FDZZ API", version="6.0.0", default_response_class=ORJSONResponse)

app.include_router(qaa.router)
app.include_router(school.router)
app.include_router(sfw.router)
app.include_router(file.router)

@app.get("/")
async def main():
    return FileResponse("static/index.html")

@app.get("/style.css")
async def main_sytle():
    return FileResponse("static/style.css")

@app.get("/status")
async def status():
    return PlainTextResponse("Hi!")

@app.get('/ip')
async def ip(ip: str = Header(None, alias='X-Forwarded-For')):
    return PlainTextResponse(content=f"{ip}")

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
