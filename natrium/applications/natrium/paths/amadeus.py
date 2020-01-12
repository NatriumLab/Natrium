# for <Steins;Gate>'s Makise Kurisu, el psy congroo :)
from fastapi import UploadFile, File, BackgroundTasks, Query
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
import maya
from i18n import t as Ts_

def Save(image, Hash):
    image.save(f"./assets/resources/{Hash}.png", "PNG")

@router.post(
    "/amadeus/upload/{name}",
#    dependencies=[Depends(depends.Permissison("Normal"))],
    tags=['Amadeus'],
    summary=Ts_("apidoc.natrium.amadeus_uploader.summary"),
    description=Ts_("apidoc.natrium.amadeus_uploader.description")
)
async def amadeus_upload(
        bgTasks: BackgroundTasks,

        file: UploadFile = File(...),
        name: str = Query(..., min_length=4, max_length=60, regex=res.ResourceName),

        Model: enums.MCTextureModel = Query("auto", alias="model"),
        Type: enums.MCTextureType = Query(..., alias="type"),
        
        Private: bool = False,
        Protect: bool = False,

        uploader: Account = Depends(depends.AccountFromRequestForm(alias="auth"))
    ):
    """参数name为要创建的资源名称.\n 
    通过表单API上传图片, 名称"file"\n
    通过表单发送认证, 名称"auth".\n

    可用get query传参: \n
    
    ``` url
    http://127.0.0.1:8000/natrium/amadeus/upload/aResourceName?type=skin&strict=true&model=alex
    ```
    """
    # 常量分配
    Original: bool = True # 在库中是否是第一个被创建的
    OriginalResource: Optional[Resource] = None
    OriginalUploader: Optional[Account] = None

    if Private and Protect:
        raise exceptions.DuplicateRegulations()

    image: Image = Image.open(BytesIO(await file.read()))
    width, height = image.size

    if height > config['natrium']['upload']['picture-size']['height'] or\
        width > config['natrium']['upload']['picture-size']['width']:
        raise exceptions.NonCompliantMsg()

    image.resize((
        int(width / 22) * 32 if width % 22 == 0 else width,
        int(width / 17) * 32 if height % 17 == 0 else height
    ))

    pictureContentHash = hashing.PicHash(image)

    with orm.db_session:
        attempt_select = orm.select(i for i in Resource if i.PicHash == pictureContentHash)
        if attempt_select.exists():
            # 如果真的有上传的数据一样的
            Original = False
            for i in attempt_select[:]:
                # 询问数据库, 找到原始作者
                # 考虑加入uploader找寻.
                if not i.Origin:
                    OriginalResource = i
                    OriginalUploader = i.Owner
                    break

            if not OriginalResource or\
                not OriginalUploader: # 判断是否找到了, 如果没找到, 说明数据库信息受损
                raise exceptions.BrokenData({
                    "PictureHash": pictureContentHash,
                    "ExceptionRaisedTime": maya.now()
                })
            # 如果有attempt_select, 就一定有一个origin.

            # 判断是否是原作者闲着没事干, 重新上传了一个.
            if OriginalUploader.Id == uploader.Id:
                raise exceptions.OccupyExistedAddress({
                    "originalResource": {
                        "id": OriginalResource.Id,
                        "owner": OriginalUploader.Id
                    },
                    "uploader": {
                        "id": uploader.Id
                    }
                })
            else: # ...或者是其他人, 这种情况我们需要特殊处理
                # 由于Protect的受限度较低, 故放在上面点.
                if OriginalResource.Protect:
                    if Protect or Private:
                        raise exceptions.PermissionDenied({
                            "originalResource": {
                                "id": OriginalResource.Id,
                                "owner": OriginalUploader.Id,
                                "protect": OriginalResource.Protect,
                                "private": OriginalResource.Private
                            },
                            "uploader": {
                                "id": uploader.Id
                            }
                        })
                    else: # 但是你本来就可以设为这个啊, 为啥要自己整一路去?
                        raise exceptions.OccupyExistedAddress({
                            "originalResource": {
                                "id": OriginalResource.Id,
                                "owner": OriginalUploader.Id,
                                "protect": OriginalResource.Protect,
                            },
                            "uploader": {
                                "id": uploader.Id
                            }
                        })
                elif OriginalResource.IsPrivate:
                    # 如果私有, 则不允许任何人上传/使用/设保护/私有等
                    raise exceptions.OccupyExistedAddress({
                        "originalResource": {
                            "id": OriginalResource.Id,
                            "owner": OriginalUploader.Id,
                            "protect": OriginalResource.Protect,
                        },
                        "uploader": {
                            "id": uploader.Id
                        }
                    })
                else:
                    # 你什么私有保护什么的都没开? 别开你自己的私有保护什么的就OK.
                    if Protect or Private:
                        raise exceptions.PermissionDenied({
                            "originalResource": {
                                "id": OriginalResource.Id,
                                "owner": OriginalUploader.Id
                            },
                            "uploader": {
                                "id": uploader.Id
                            },
                            "options": {
                                'protect': Protect,
                                "private": Private
                            }
                        })
                    else:
                        # 找寻上传者是否也曾经上传过该材质
                        assert_the_same = orm.select(i for i in Resource\
                            if i.PicHash == pictureContentHash and \
                            i.Owner.Id == uploader.Id)
                        if assert_the_same.exists():
                            ats_first: Resource = assert_the_same.first()
                            raise exceptions.OccupyExistedAddress({
                                "ownedResource": {
                                    "id": ats_first.Id,
                                    "name": ats_first.Name
                                },
                                "uploader": {
                                    "id": uploader.Id
                                }
                            })
                        

        if Model == "auto":
            Model = ['steve', 'alex'][skin.isSilmSkin(image)]

        account = Account.get(Id=uploader.Id)
        resource = Resource(
            PicHash = pictureContentHash,
            Name = name,
            PicHeight = height, PicWidth = width,
            Model = Model, Type = Type,
            Owner = account,
            IsPrivate = Private, Protect = Protect,
            Origin = OriginalResource
        )
        if Original:
            bgTasks.add_task(Save, image, pictureContentHash)
        orm.commit()
        return {
            "operator": "success",
            "metadata": resource.format_self(requestHash=True)
        }

