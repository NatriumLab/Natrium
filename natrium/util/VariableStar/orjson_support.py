import orjson
from starlette.responses import JSONResponse
import typing
import functools
import maya
import uuid

class OrjsonResponse(JSONResponse):
    media_type = "application/json"

    def orjson_default_render(self, content: typing.Any):
        if isinstance(content, maya.MayaDT):
            return content.rfc2822()
        elif isinstance(content, uuid.UUID):
            return content.hex

    def render(self, content: typing.Any) -> bytes:
        return orjson.dumps(content, default=self.orjson_default_render)