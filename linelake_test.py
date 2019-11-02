import natrium.lake
import asyncio
from importlib import reload

#asyncio.run(reload(natrium.lake).main())
import natrium.lake.models.line
from natrium.lake.modules.Line import LineLake

async def main():
    import uuid
    p = await LineLake.Create()
    await p.Select()
    class test1:
        Id = uuid.uuid4()
    class test2:
        Id = uuid.uuid4()
    to1 = test1()
    to2 = test2()

    Master1Token = await p.CreateMasterByObject(to1)
    print(await p.SaveObject(
        Master1Token.format()
    ))
    Forked1Token = await Master1Token.fork()
    print(await p.SaveObject(Forked1Token.format()))
    print(await p.QueryLine(Forked1Token.AccessToken, Forked1Token.ClientToken))
    User1Lines = await p.QueryAccountLines(to1.Id)

    Master2Token = await p.CreateMasterByObject(to2)
    print(await p.SaveObject(
        Master2Token.format()
    ))
    Forked2Token = await Master2Token.fork()
    print(await p.SaveObject(Forked2Token.format()))
    print(await p.QueryLine(Forked2Token.AccessToken, Forked2Token.ClientToken))
    User2Lines = await p.QueryAccountLines(to2.Id)

    print(len(User1Lines))
    print(len(User2Lines))

asyncio.run(main())