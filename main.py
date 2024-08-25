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


@app.get("/ip")
async def get_ip(request: Request):
    client_host = request.headers.get("X-Real-IP")
    if not client_host:
        client_host = request.client.host
    return PlainTextResponse(client_host)
