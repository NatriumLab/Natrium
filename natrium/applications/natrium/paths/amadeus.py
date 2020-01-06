# for <Steins;Gate>'s Makise Kurisu, el psy congroo :)
from fastapi import UploadFile, File, BackgroundTasks
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
from pathlib import Path
import aiofiles

def Save(image, Hash):
    image.save(f"./assets/resources/{Hash}.png", "PNG")

@router.post(
    "/amadeus/upload/{name}",
    dependencies=[Depends(depends.Permissison("Normal"))]
)
async def amadeus_upload(
        name: str, bgTasks: BackgroundTasks,
        strict: bool = True,

        file: UploadFile = File(...),
        Type: enums.MCTextureType = "auto",
        Model: enums.MCTextureModel = "auto",
        Private: bool = False, Protect: bool = False,

        uploader: Account = Depends(depends.AccountFromRequest)
    ):
    Origin = None
    result = {}
    if not res.verify(name, res.ResourceName):
        raise exceptions.NonCompliantMsg()
    with BytesIO() as b:
        try:
            b.write(await file.read())
            image: Image = Image.open(b)
        except PIL.UnidentifiedImageError:
            raise exceptions.UnrecognizedContent()
    picHash = hashing.PicHash(image)

    with orm.db_session:
        #attept = Resource.get(PicHash=picHash)
        attept = orm.select(i for i in Resource if i.PicHash == picHash)
        if attept.exists():
            for i in list(attept):
                if not i.IsPrivate: # 如果私有
                    if Protect: # ?还想设置保护?
                        raise exceptions.PermissionDenied()
                    if not Private: # 我都说了, 只能自己偷偷用.
                        raise exceptions.OccupyExistedAddress()
                if i.Protect and not Private:
                    # 源作者设置保护, 将不能以公开形式上传.(只能自己偷偷用.)
                    if strict: # 是否严格
                        raise exceptions.OccupyExistedAddress()
                    else: # 不严格就自动设置为Private
                        result.update({
                            "warnings": []
                        })
                        result['warnings'].append({
                            "type": "ProtectedResource",
                            "message": "Because the source author has set up protection for this resource, \
                                and you have not used strict mode, \
                                    the resources you upload can only be used for your own use.",
                            "metadata": {
                                "origin": i.Id
                            }
                        })
                        Private = True
                        Origin = i

        width = image.size[0]
        height = image.size[1]

        if height > config['natrium']['upload']['picture-size']['height'] or\
            width > config['natrium']['upload']['picture-size']['width']:
            raise exceptions.NonCompliantMsg

        image.resize((
            int(width / 22) * 32 if width % 22 == 0 else width,
            int(width / 17) * 32 if height % 17 == 0 else height
        ))

        if Type == "auto":
            Type = ["skin", "cape"][skin.isCape(image)]
    
        if Model == "auto":
            Model = ['steve', 'alex'][skin.isSilmSkin(image)]
    
        account = Account.get(Id=uploader.Id)
        resource = Resource(
            PicHash = picHash,
            Name = name,
            PicHeight = height, PicWidth = width,
            Model = Model, Type = Type,
            Owner = account,
            IsPrivate = Private
        )
        if Origin:
            resource.Origin = Origin
        else:
            # yysy, 这确实是你上传的.jpg
            bgTasks.add_task(Save, image, picHash)
        orm.commit()
        result.update({
            "operator": "success",
            "metadata": resource.format_self(requestHash=True)
        })
        return result