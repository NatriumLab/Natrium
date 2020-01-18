"""
Inspired by : \n
  skinview3d(https://github.com/bs-community/skinview3d)  \n
  skinview-utils(https://github.com/yushijinhun/skinview-utils)  \n
Python Port by NatriumLab.  
"""
from PIL import Image, ImageDraw

def hasTransparency(context: Image.Image, x1, y1, w, h):
    """判断一个块是否不是透明的"""
    img = context.crop((x1, y1, x1+w, y1+h)) # 裁下一块来
    for x in range(w):
        for y in range(h):
            if img.getpixel((x, y))[3] == 0: # 判断是否是空(A是0), 如果是这个块就是透明的.
                return False
            #print(listget(imgData, offset + 3))
    return True

def computeSkinScale(width):
    return int(width / 64)

def isSilmSkin(context: Image.Image):
    scale = computeSkinScale(context.size[0])
    # context.size[0] 即 width, 此处可能是用于高分辨率资源的缩放比例计算.
    checkArea = lambda x, y, w, h: \
        hasTransparency(context, x * scale, y * scale, w * scale, h * scale)
    # hasTransparency这个函数判断块是否是空的

    return not (
        checkArea(50, 16, 2, 4) | 
        checkArea(54, 20, 2, 12) | 
        checkArea(42, 48, 2, 4) | 
        checkArea(46, 52, 2, 12)
    )
    # 原本这里是用于检查steve模型的吧(笑), 去掉not就又是另外一个函数了

def fixOpaqueSkin(context: Image.Image, width: int):
    if not hasTransparency(context, 0, 0, width, int(width / 2)):
        scale = computeSkinScale(width)
        contextDraw: ImageDraw.ImageDraw = ImageDraw.Draw(context)
        for x, y, w, h in [
                (40, 0, 8, 8), # Helm Top
                (48, 0, 8, 8), # Helm Bottom
                (32, 8, 8, 8), # Helm Right
                (40, 8, 8, 8), # Helm Front
                (48, 8, 8, 8), # Helm Left
                (56, 8, 8, 8)  # Helm Back
            ]:
            contextDraw.rectangle(
                xy=[
                    (x * scale, y * scale),
                    (
                        (x + w) * scale,
                        (y + h) * scale
                    )
                ],
                width=0, # 防止绘出矩形轮廓
                fill=(255, 255, 255, 0)
            )

def resize_without_zoom(context, box):
    i = Image.new("RGBA", box)
    i.paste(context)
    return i

def checkOpaqueSkin(context: Image.Image, width: int) -> bool:
    return hasTransparency(context, 0, 0, width, int(width / 2))

def flipHorizontal_func(image: Image.Image):
    return image.transpose(Image.FLIP_LEFT_RIGHT)

def copyImage(context: Image.Image, sX: int, sY: int, w: int, h: int, dX: int, dY: int, flipHorizontal: bool):
    img = context.crop((sX, sY, sX+w, sY+h))
    if flipHorizontal:
        img = flipHorizontal_func(img)
    context.paste(img, (dX, dY))

def convertSkinTo1_8(context: Image.Image, width: int):
    scale = computeSkinScale(width)
    context = resize_without_zoom(context, (width, width))

    fixOpaqueSkin(context, width)

    args = [
        (4, 16, 4, 4, 20, 48, True),
        (8, 16, 4, 4, 24, 48, True),
        (0, 20, 4, 12, 24, 52, True),
        (4, 20, 4, 12, 20, 52, True),
        (8, 20, 4, 12, 16, 52, True),
        (12, 20, 4, 12, 28, 52, True),
        (44, 16, 4, 4, 36, 48, True),
        (48, 16, 4, 4, 40, 48, True),
        (40, 20, 4, 12, 40, 52, True),
        (44, 20, 4, 12, 36, 52, True),
        (48, 20, 4, 12, 32, 52, True),
        (52, 20, 4, 12, 44, 52, True)
    ]
    for i in args:
        copyImage(context, *[k*scale for k in i[:-1]], i[-1])
    return context

def convertSkinTo1_8_auto(context: Image.Image):
    return convertSkinTo1_8(context, context.width)

def getblock(context: Image.Image, box, scale):
    return context.crop((
        box[0]*scale*8,
        box[1]*scale*8,
        (box[0]+1)*scale*8,
        (box[1]+1)*scale*8
    ))

def gethead(context: Image.Image):
    scale = computeSkinScale(context.width)
    head = getblock(context, (1, 1), scale)
    heat = getblock(context, (5, 1), scale)
    head.paste(heat, (0, 0), heat.getchannel("B"))
    return head

if __name__ == "__main__":
    from PIL import Image
    assert isSilmSkin(Image.open("./assets/resources/81c26f889ba6ed12f97efbac639802812c687b4ffcc88ea75d6a8d077328b3bf.png")) == False
    assert isSilmSkin(Image.open("./assets/resources/490bd08f1cc7fce67f2e7acb877e5859d1605f4ffb0893b07607deae5e05becc.png")) == True
    me: Image.Image = Image.open("./assets/resources/81c26f889ba6ed12f97efbac639802812c687b4ffcc88ea75d6a8d077328b3bf.png")
    #fixOpaqueSkin(me, 64)
    gethead(convertSkinTo1_8_auto(me)).show()