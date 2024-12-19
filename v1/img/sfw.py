import random
from fastapi import APIRouter, HTTPException
from fastapi.responses import ORJSONResponse
import httpx

router = APIRouter(prefix="/img", tags=["img"])

# 데이터를 상수로 분리
OPTIONAL_ACTIONS = [
    "waifu",
    "neko",
    "shinobu",
    "megumin",
    "bully",
    "cuddle",
    "cry",
    "hug",
    "awoo",
    "kiss",
    "lick",
    "pat",
    "smug",
    "bonk",
    "yeet",
    "blush",
    "smile",
    "wave",
    "highfive",
    "handhold",
    "nom",
    "bite",
    "glomp",
    "slap",
    "kill",
    "kick",
    "happy",
    "wink",
    "poke",
    "dance",
    "cringe",
]


@router.get("/sfw")
async def sfw() -> ORJSONResponse:
    """
    Asynchronously retrieves a URL to a safe-for-work (sfw) anime-related image from an external API. The
    function randomly selects an action from pre-defined options and utilizes an HTTP client to make a request
    to the API. Based on the response, it either returns the fetched URL or raises an appropriate HTTP
    exception. This is intended for safe-for-work use cases related to fetching anime-themed content.

    :return: JSON response containing the URL of the fetched sfw image.
    :rtype: ORJSONResponse

    :raises HTTPException: If an error occurs while processing the external API response.
    :raises HTTPException: If the external API call fails with a status code other than OK (200).
    """
    # 무작위 선택
    selected_action = random.choice(OPTIONAL_ACTIONS)

    # 외부 API 호출
    api_url = f"https://api.waifu.pics/sfw/{selected_action}"
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url)

    # 응답 상태 코드 확인
    if response.status_code == httpx.codes.OK:
        try:
            # JSON 데이터 파싱
            data = response.json()
            return ORJSONResponse(content={"url": data.get("url", "")}, status_code=200)
        except Exception:
            # JSON 파싱 오류 처리
            raise HTTPException(
                status_code=500, detail="Error processing external API response."
            )
    else:
        # 외부 API 호출 실패
        raise HTTPException(
            status_code=response.status_code,
            detail="Failed to fetch data from external API.",
        )
