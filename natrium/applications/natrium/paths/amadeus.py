# for <Steins;Gate>'s Makise Kurisu, el psy congroo :)
from fastapi import UploadFile, File
from fastapi import Depends
from .. import depends
from .. import router
from .. import exceptions
import uuid
from pony import orm
from typing import Optional
from natrium.database.models import Account, Resource, Character
from .. import models
from PIL import Image, ImageDraw
from io import BytesIO
from conf import config
import PIL
from natrium.util import enums, skin, hashing, res

@router.post(
    "/amadeus/upload/{name}",
    dependencies=[Depends(depends.Permissison("Normal"))]
)
async def amadeus_upload(
        name: str,
        file: UploadFile = File(...),
        Type: enums.MCTextureType = "auto",
        Model: enums.MCTextureModel = "auto",
        Private: bool = False,

        uploader: Account = Depends(depends.AccountFromRequest)
    ):
    if not res.verify(name, res.ResourceName):
        raise exceptions.NonCompliantMsg()
    with BytesIO() as b:
        try:
            b.write(await file.read())
            image: Image = Image.open(b)
        except PIL.UnidentifiedImageError:
            raise exceptions.UnrecognizedContent()

    width = image.size[0]
    height = image.size[1]

    if height > config['natrium']['upload']['picture-size']['height'] or\
        width > config['natrium']['upload']['picture-size']['width']:
        raise exceptions.NonCompliantMsg

    image.resize(
        (int(width / 22) * 32 if width % 22 == 0 else width,
        int(width / 17) * 32 if height % 17 == 0 else height)
    )

    if Type == "auto":
        Type = ["skin", "cape"][skin.isCape(image)]
    
    if Model == "auto":
        Model = ['steve', 'alex'][skin.isSilmSkin(image)]

    with orm.db_session:
        account = Account.get(Id=uploader.Id)
        resource = Resource(
            PicHash = hashing.PicHash(image),
            Name = name,
            PicHeight = height, PicWidth = width,
            Model = Model, Type = Type,
            Owner = account,
            IsPrivate = Private
        )
        orm.commit()
        return {
            "operator": "success",
            "metadata": resource.format_self(requestHash=True)
        }