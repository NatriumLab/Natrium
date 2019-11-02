from enum import Enum
from .enums import MCTextureType, MCTextureModel

class ResourceMetadata(object):
    @staticmethod
    def MCTexture(
        type: MCTextureType = MCTextureType.skin, 
        model: MCTextureModel = MCTextureModel.steve) -> dict:
        return {
            "type": "MinecraftTexture",
            "body": {
                "type": type.value,
                "model": model.value
            }
        }
