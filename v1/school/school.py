from main import *
from src.function import *
from src.schema import *
import requests

router = APIRouter(prefix="/v1/school", tags=["school"])


# noinspection SpellCheckingInspection,PyUnboundLocalVariable
@router.post("/meal", description="날자 형식: yyyy-mm-dd, ex) 2024-06-17")
async def meal_info(body: SchemaMealInfo):
    url = f"https://open.neis.go.kr/hub/schoolInfo?KEY={OPEN_NEIS_API_KEY}&Type=json&pIndex=1&pSize=10&SCHUL_NM={body.school_name}"
    request = requests.get(url=url)
    r = orjson.loads(request.text)
    rr = r['schoolInfo'][-1]
    rrr = rr['row'][-1]
    atpt_ofcdc_sc_code = rrr['ATPT_OFCDC_SC_CODE']
    sd_schul_code = rrr['SD_SCHUL_CODE']
    print(atpt_ofcdc_sc_code)
    print(sd_schul_code)

    if body.date:
        body.date = DATE

    url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?KEY={OPEN_NEIS_API_KEY}&Type=json&pIndex=1&pSize=10&ATPT_OFCDC_SC_CODE={atpt_ofcdc_sc_code}&SD_SCHUL_CODE={sd_schul_code}&MLSV_FROM_YMD={body.date}&MLSV_TO_YMD={body.date}"
    request = requests.get(url=url)
    if request.text == """{"RESULT":{"CODE":"INFO-200","MESSAGE":"해당하는 데이터가 없습니다."}}""":
        return ORJSONResponse(content={"RESULT": {"CODE": "INFO-200", "MESSAGE": "해당하는 데이터가 없습니다."}}, status_code=200)
    else:
        r = orjson.loads(request.text)
        rr = r['mealServiceDietInfo'][-1]
        rrr = rr['row'][-1]
        ddish_nm = rrr['DDISH_NM']
        ddish_nm_list = ddish_nm.replace('<br/>', '\n')
        return ORJSONResponse(content={"SchoolName": f"{body.school_name}", "SchoolMeal": [ddish_nm_list]},
                              status_code=200)


@router.post("/class_time")
async def class_time(body: SchemaClassTimeInfo):
    return ORJSONResponse(content={"준비중": body})
