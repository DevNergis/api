from main import *
from src.function import *
from src.schema import *

router = APIRouter(prefix="/v1/h-k", tags=["han-cho"])

@router.get("/sfw")
async def api_img():
    return ORJSONResponse(content={"info": f"오늘은 코체가 한강물을 {random.randint(1, 100)}% 만큼 먹었어요!"})
