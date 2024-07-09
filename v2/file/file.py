from fastapi import *

router = APIRouter(prefix="/file", tags=["file"])


@router.get("/test")
async def asdad():
    return "asd"
