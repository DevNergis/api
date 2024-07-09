from fastapi import *

from .file import file

router = APIRouter(prefix="/v2", tags=["v2"])

router.include_router(file.router)
