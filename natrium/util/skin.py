"""
Inspired by skinview3d(https://github.com/bs-community/skinview3d)
Python Port by NatriumLab.
"""
from PIL import Image

def hasTransparency(context: Image, x1, y1, w, h):
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

def isSilmSkin(context: Image):
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

def isCape(context: Image):
    scale = computeSkinScale(context.size[0])
    checkArea = lambda x, y, w, h: \
        hasTransparency(context, x * scale, y * scale, w * scale, h * scale)
    result = [
        (not checkArea(0, 0, 1, 1)), # 断言 0, 0 是透明.
        (not checkArea(0, 21, 1, 1)),
        checkArea(1, 0, 20, 1),
        checkArea(0, 1, 1, 16),
        checkArea(1, 1, 10, 16),
        checkArea(11, 1, 1, 16),
        checkArea(12, 1, 10, 16)
    ]
    return all(result)

if __name__ == "__main__":
    from PIL import Image
    assert isSilmSkin(Image.open("./assets/resources/81c26f889ba6ed12f97efbac639802812c687b4ffcc88ea75d6a8d077328b3bf.png")) == False
    assert isSilmSkin(Image.open("./assets/resources/490bd08f1cc7fce67f2e7acb877e5859d1605f4ffb0893b07607deae5e05becc.png")) == True
    assert isCape(Image.open("./assets/resources/ddcf7d09723e799e59d7f19807d0bf5e3a2c044ce17e76a48b8ac4d27c0b16e0.png")) == True
    assert isCape(Image.open("./assets/resources/81c26f889ba6ed12f97efbac639802812c687b4ffcc88ea75d6a8d077328b3bf.png")) == False