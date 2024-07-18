from fastapi import *
from fastapi.responses import *
from starlette.middleware.cors import CORSMiddleware

import v1
import v2

app = FastAPI(
    title="Nergis API",
    summary="Made By Dev_Nergis",
    description="Nergis API",
    version="7.3.6",
    default_response_class=ORJSONResponse)

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1.router)
app.include_router(v2.router)


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
