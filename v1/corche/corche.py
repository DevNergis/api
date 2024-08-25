import random

from fastapi import *
from fastapi.responses import *

router = APIRouter(prefix="/corche", tags=["corche"])


@router.get("/today_H_corche")
async def today_h_corche():
    return ORJSONResponse(content={"info": f"오늘은 코체가 한강물을 {random.randint(1, 100)}% 만큼 먹었어요!"})


@router.get("/today_corche")
async def today_corche():
    q = ["오늘 코체의 기분은 어때?", "오늘 코체는 얼마나 멍청 한가요?"]
    a = ["좋아요!", "나뻐요!", "멍청해요!"]

    return ORJSONResponse(content={"q": random.choice(q), "a": random.choice(a)})
