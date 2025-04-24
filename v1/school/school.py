from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from src.function import *
from src.schema import SchemaMealInfo, SchemaClassTimeInfo
import requests
import orjson

router = APIRouter(prefix="/school", tags=["school"])

# Constants
OPEN_NEIS_BASE_URL = "https://open.neis.go.kr/hub"
NO_DATA_MESSAGE = {
    "RESULT": {"CODE": "INFO-200", "MESSAGE": "해당하는 데이터가 없습니다."}
}


def build_neis_url(endpoint: str, **params: str) -> str:
    """
    Constructs a complete URL for the NEIS API using the provided endpoint and query parameters.

    This function takes an API endpoint and additional query parameters to
    build a full URL string for making requests to the NEIS API. Each parameter
    is appended to the endpoint as part of the query string in key=value format,
    joined by ampersands.

    :param endpoint: The specific API endpoint to be accessed.
    :type endpoint: str
    :param params: Additional query parameters to be included in the URL.
    :type params: dict[str, str]
    :return: A fully constructed URL string for the NEIS API, containing the
        endpoint and any provided query parameters.
    :rtype: str
    """
    query = "&".join([f"{key}={value}" for key, value in params.items()])
    return f"{OPEN_NEIS_BASE_URL}/{endpoint}?{query}"


def get_orjson_response(content: dict, status_code: int = 200) -> ORJSONResponse:
    """
    Generates an ORJSONResponse using the provided content and status code.

    This function produces an instance of ORJSONResponse by taking a dictionary of
    content and an optional HTTP status code. If no status code is explicitly
    provided, it defaults to 200. The ORJSON response format provides better
    performance and tighter integration with JSON handling in Python.

    :param content: Dictionary containing the response data.
    :type content: dict
    :param status_code: HTTP status code for the response. Defaults to 200.
    :type status_code: int, optional
    :return: An ORJSONResponse populated with the given content and status code.
    :rtype: ORJSONResponse
    """
    return ORJSONResponse(content=content, status_code=status_code)


@router.post("/meal", description="날자 형식: yyyy-mm-dd, ex) 2024-06-17")
async def meal_info(body: SchemaMealInfo) -> ORJSONResponse:
    """
    Handles the '/meal' POST route, which fetches meal-related information for a given
    school and date. The input is provided through the request payload and includes
    details such as the school name and an optional date. The default date is set to
    the current date if not provided. It uses the Open NEIS API to retrieve school
    and meal data, and returns the formatted response in ORJSON format.

    :param body: An instance of SchemaMealInfo containing the school name and
        optional meal date in the format 'yyyy-mm-dd'.
    :type body: SchemaMealInfo

    :return: An ORJSONResponse containing the school name and formatted meal data
        or a predefined "no data" message if no meal information is available.
    :rtype: ORJSONResponse

    :raises HTTPException: If the Open NEIS API fails to return valid data or encounters
        other issues during the request/response lifecycle.
    """
    if body.date is None:
        body.date = DATE  # Default to the current date.

    # Fetch school information
    school_info_url = build_neis_url(
        "schoolInfo",
        KEY=OPEN_NEIS_API_KEY,
        Type="json",
        pIndex="1",
        pSize="10",
        SCHUL_NM=body.school_name,
    )
    school_response = requests.get(url=school_info_url)
    school_data = orjson.loads(school_response.text).get("schoolInfo", [-1])[-1]
    school_detail = school_data["row"][-1]  # Extract school detail row.

    atpt_ofcdc_sc_code = school_detail["ATPT_OFCDC_SC_CODE"]
    sd_schul_code = school_detail["SD_SCHUL_CODE"]

    # Fetch meal information
    meal_info_url = build_neis_url(
        "mealServiceDietInfo",
        KEY=OPEN_NEIS_API_KEY,
        Type="json",
        pIndex="1",
        pSize="10",
        ATPT_OFCDC_SC_CODE=atpt_ofcdc_sc_code,
        SD_SCHUL_CODE=sd_schul_code,
        MLSV_FROM_YMD=body.date,
        MLSV_TO_YMD=N_DATE,
    )
    meal_response = requests.get(url=meal_info_url)

    # Check for no data response
    if meal_response.text == orjson.dumps(NO_DATA_MESSAGE).decode():
        return get_orjson_response(NO_DATA_MESSAGE)

    meal_data = orjson.loads(meal_response.text).get("mealServiceDietInfo", [-1])[-1]
    meal_detail = meal_data["row"][-1]["DDISH_NM"]
    formatted_meal = meal_detail.replace("<br/>", "\n")

    return get_orjson_response(
        {
            "SchoolName": body.school_name,
            "SchoolMeal": [formatted_meal],
        }
    )


@router.post("/class_time")
async def class_time(body: SchemaClassTimeInfo) -> ORJSONResponse:
    """
    Handles the POST request for class time information and processes the given
    data according to the specified schema. Returns a JSON response indicating
    the status or result of the operation.

    :param body: Incoming request body containing class time information as
        specified by the `SchemaClassTimeInfo` schema.
    :type body: SchemaClassTimeInfo
    :return: A JSON response constructed using ORJSON indicating the operation
        result or status with the provided body data.
    :rtype: ORJSONResponse
    """
    return get_orjson_response({"준비중": body})
