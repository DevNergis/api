from fastapi import *

from .file import file
from .folder import folder
from .cipher import cipher
from .school import school

router = APIRouter(prefix="/v2", tags=["v2"])

router.include_router(file.router)
router.include_router(folder.router)
router.include_router(cipher.router)
router.include_router(school.router)
