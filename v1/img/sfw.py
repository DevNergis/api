import random

from main import *

router = APIRouter(prefix="/v1/img", tags=["img"])


@router.get("/sfw")
async def api_img():
    import requests
    optional = random.choice(
        ["waifu", "neko", "shinobu", "megumin", "bully", "cuddle", "cry", "hug", "awoo", "kiss", "lick", "pat", "smug",
         "bonk", "yeet", "blush", "smile", "wave", "highfive", "handhold", "nom", "bite", "glomp", "slap", "kill",
         "kick", "happy", "wink", "poke", "dance", "cringe"])
    sfw = requests.get(f"https://api.waifu.pics/sfw/{optional}")
    if (sfw.status_code == requests.codes.ok):
        sfw = sfw.json()
        sfw = sfw["url"]
        print(sfw)
        return ORJSONResponse(content={"url": f"{sfw}"}, status_code=200)
