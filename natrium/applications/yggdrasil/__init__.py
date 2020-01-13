from fastapi import APIRouter

router = APIRouter()

# 子模块
import natrium.applications.yggdrasil.authserver
import natrium.applications.yggdrasil.sessionserver
import natrium.applications.yggdrasil.utils