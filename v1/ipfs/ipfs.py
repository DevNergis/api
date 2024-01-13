from main import *
from src.function import *
from src.schema import *
from math import ceil
from io import BytesIO
import aiohttp

router = APIRouter(prefix="/v1/ipfs", tags=["ipfs"])

@router.post("/upload")
async def ipfs_upload(files: List[UploadFile] = File()):
    file_size_list = list()
    file_name_list = list()
    file_direct_list = list()

    header = {
        'x-agent-did': x_agent_did,
        'Authorization': Authorization
    }

    file_list = aiohttp.FormData()

    for file in files:
        chunk = BytesIO()
        chunk_range = range(ceil(file.size / (1024*1024*2)))
        
        for _ in chunk_range:
            chunk.write(await file.read(1024*1024*2))

        chunk.seek(0)

        file_list.add_field(name="file", value=chunk.read(), content_type="application/octet-stream", filename=file.filename)

        file_size_list.append(file.size)
        file_name_list.append(file.filename)

    async with aiohttp.ClientSession(headers=header) as session:
        async with session.post("https://api.nft.storage/upload", data=file_list) as response:
            try:
                data = await response.json()
                cid = data["value"]["cid"]
                directory_url = f"https://{cid}.ipfs.cf-ipfs.com"
                for file_name in file_name_list:
                    file_direct_list.append(f"https://{cid}.ipfs.cf-ipfs.com/{file_name}")
            except:
                pass

    if response.status == 200:
        return ORJSONResponse(content={"file_size": file_size_list, "directory_cid": cid, "file_name": file_name_list, "directory_url": directory_url, "file_direct": file_direct_list}, status_code=200)
    else:
        return PlainTextResponse(content=await response.read(), status_code=response.status)
