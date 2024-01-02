from typing import *
import random, orjson
from datetime import *
from fastapi import *
from fastapi.responses import *
from fastapi.middleware.cors import *
from src.function import *
from src.schema import *
import base64, requests, uuid, re

from api.v1.qloat import qaa
from api.v1.school import school
from api.v1.img import sfw
from api.v1.file import file
from api.v1.ipfs import ipfs

app = FastAPI(
    title="Nergis API",
    summary="Made By Dev_Nergis",
    description="Nergis API",
    version="7.3.5",
    default_response_class=ORJSONResponse)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 

app.include_router(qaa.router)
app.include_router(school.router)
app.include_router(sfw.router)
app.include_router(file.router)
app.include_router(ipfs.router)

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
