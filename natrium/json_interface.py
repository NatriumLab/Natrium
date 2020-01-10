from starlette.responses import JSONResponse
import json

# 选择需要使用的JSON序列化包.
def try_import(package):
    try:
        pack = __import__(package)
    except (ModuleNotFoundError, ImportError):
        return None
    else:
        return pack

selected_jsonencoder = JSONResponse
handler = json

ujson_try = try_import("ujson")
if ujson_try:
    from starlette.responses import UJSONResponse
    selected_jsonencoder = UJSONResponse
    handler = ujson_try

orjson_try = try_import("orjson")
if orjson_try:
    from .util.VariableStar.orjson_support import OrjsonResponse
    selected_jsonencoder = OrjsonResponse
    handler = orjson_try