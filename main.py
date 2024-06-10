from fastapi import *
from fastapi.responses import *
from starlette.middleware.cors import CORSMiddleware

from src.function import ydl_url
from v1.corche import corche
from v1.file import file
from v1.img import sfw
from v1.ipfs import ipfs
from v1.qloat import qaa
from v1.school import school

app = FastAPI(
    title="Nergis API",
    summary="Made By Dev_Nergis",
    description="Nergis API",
    version="7.3.6",
    default_response_class=ORJSONResponse,
    debug=True)

# noinspection PyTypeChecker
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
app.include_router(corche.router)


@app.get("/")
async def main():
    return FileResponse("static/index.html")


@app.get("/style.css")
async def main_style():
    return FileResponse("static/style.css")


@app.get("/status")
async def status():
    return PlainTextResponse("Hi!")


# noinspection PyShadowingNames
@app.get('/ip')
async def ip(ip: str = Header(None, alias='X-Forwarded-For')):
    return PlainTextResponse(content=f"{ip}")


@app.get("/yt-dla")
async def youtube_dl(url: str):
    url = ydl_url(url)

    return HTMLResponse(content=f"""{url}""", status_code=200)
