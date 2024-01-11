from main import *
from src.function import *
from src.schema import *

router = APIRouter(prefix="/v1/ipfs", tags=["ipfs"])

@router.post("/upload")
async def ipfs_upload(files: List[UploadFile] = File()):
    import requests

    file_size_list = list()
    file_name_list = list()
    file_direct_list = list()

    header = {
        'x-agent-did': x_agent_did,
        'Authorization': Authorization
    }

    file_list = list()

    for file in files:
        file_list.append(('file', (file.filename, file.file.read(20*1024*1024), 'application/octet-stream')))

        file_size_list.append(file.size)
        file_name_list.append(file.filename)

    response = requests.post("https://api.nft.storage/upload", files=file_list, headers=header)
    data = response.json()

    cid = data["value"]["cid"]
    directory_url = f"https://{cid}.ipfs.cf-ipfs.com"

    for file_name in file_name_list:
        file_direct_list.append(f"https://{cid}.ipfs.cf-ipfs.com/{file_name}")

    if response.status_code == 200:
        return ORJSONResponse(content={"file_size": file_size_list, "directory_cid": cid, "file_name": file_name_list, "directory_url": directory_url, "file_direct": file_direct_list}, status_code=200)
