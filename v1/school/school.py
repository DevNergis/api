from main import *
from src.function import *
from src.schema import *

router = APIRouter(prefix="/v1/school", tags=["school"])

@router.post("/meal")
async def mealServiceDietInfo(body: mealServiceDietInfo_):
    import requests

    url = f"https://open.neis.go.kr/hub/schoolInfo?KEY={OPEN_NEIS_API_KEY}&Type=json&pIndex=1&pSize=10&SCHUL_NM={body.SchoolName}"
    request = requests.get(url=url)
    r = orjson.loads(request.text)
    rr = r['schoolInfo'][-1]
    rrr = rr['row'][-1]
    ATPT_OFCDC_SC_CODE = rrr['ATPT_OFCDC_SC_CODE']
    SD_SCHUL_CODE = rrr['SD_SCHUL_CODE']
    url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?KEY={OPEN_NEIS_API_KEY}&Type=json&pIndex=1&pSize=10&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}&SD_SCHUL_CODE={SD_SCHUL_CODE}&MLSV_YMD={DATE}"
    request = requests.get(url=url)
    if request.text == """{"RESULT":{"CODE":"INFO-200","MESSAGE":"해당하는 데이터가 없습니다."}}""":
        return ORJSONResponse(content={"RESULT":{"CODE":"INFO-200","MESSAGE":"해당하는 데이터가 없습니다."}}, status_code=200)
    else:
        r = orjson.loads(request.text)
        rr = r['mealServiceDietInfo'][-1]
        rrr = rr['row'][-1]
        DDISH_NM = rrr['DDISH_NM']
        DDISH_NM_LIST = DDISH_NM.replace('<br/>', '\n')
        return ORJSONResponse(content={"SchoolName":f"{body.SchoolName}", "SchoolMeal":[DDISH_NM_LIST]}, status_code=200)
