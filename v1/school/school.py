from main import *
from src.function import *
from src.schema import *

router = APIRouter(prefix="/v1/school", tags=["school"])

@router.post("/meal")
async def mealservicedietinfo(body: mealservicedietinfo_):
    import requests

    url = f"https://open.neis.go.kr/hub/schoolInfo?KEY={OPEN_NEIS_API_KEY}&Type=json&pIndex=1&pSize=10&SCHUL_NM={body.SchoolName}"
    request = requests.get(url=url)
    r = orjson.loads(request.text)
    rr = r['schoolInfo'][-1]
    rrr = rr['row'][-1]
    atpt_ofcdc_sc_code = rrr['ATPT_OFCDC_SC_CODE']
    sd_schul_code = rrr['SD_SCHUL_CODE']
    url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?KEY={OPEN_NEIS_API_KEY}&Type=json&pIndex=1&pSize=10&ATPT_OFCDC_SC_CODE={atpt_ofcdc_sc_code}&SD_SCHUL_CODE={sd_schul_code}&MLSV_YMD={DATE}"
    request = requests.get(url=url)
    if request.text == """{"RESULT":{"CODE":"INFO-200","MESSAGE":"해당하는 데이터가 없습니다."}}""":
        return ORJSONResponse(content={"RESULT":{"CODE":"INFO-200","MESSAGE":"해당하는 데이터가 없습니다."}}, status_code=200)
    else:
        r = orjson.loads(request.text)
        rr = r['mealServiceDietInfo'][-1]
        rrr = rr['row'][-1]
        ddish_nm = rrr['DDISH_NM']
        ddish_nm_list = ddish_nm.replace('<br/>', '\n')
        return ORJSONResponse(content={"SchoolName":f"{body.SchoolName}", "SchoolMeal":[ddish_nm_list]}, status_code=200)
