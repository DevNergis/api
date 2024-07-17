from fastapi import *

from .corche import corche
from .file import file
from .img import sfw
from .ipfs import ipfs
from .qloat import qaa
from .school import school

router = APIRouter(prefix="/v1", tags=["v1"])

router.include_router(corche.router)
router.include_router(file.router)
router.include_router(sfw.router)
router.include_router(ipfs.router)
router.include_router(qaa.router)
router.include_router(school.router)
