import random

from fastapi import *
from fastapi.responses import *

router = APIRouter(prefix="/img", tags=["img"])


# noinspection PyShadowingNames
@router.get("/sfw")
async def sfw():
    import requests
    optional = random.choice(
        ["waifu", "neko", "shinobu", "megumin", "bully", "cuddle", "cry", "hug", "awoo", "kiss", "lick", "pat", "smug",
         "bonk", "yeet", "blush", "smile", "wave", "highfive", "handhold", "nom", "bite", "glomp", "slap", "kill",
         "kick", "happy", "wink", "poke", "dance", "cringe"])
    sfw = requests.get(f"https://api.waifu.pics/sfw/{optional}")
    if sfw.status_code == requests.codes.ok:
        sfw = sfw.json()
        sfw = sfw["url"]
        return ORJSONResponse(content={"url": f"{sfw}"}, status_code=200)
