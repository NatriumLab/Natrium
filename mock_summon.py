import natrium.database.models as M
from natrium.database.connection import db
from pony import orm
from natrium.util.hashing import OfflinePlayerUUID
from uuid import UUID
import cProfile
import asyncio
import bcrypt
from natrium import cache_pool

#print(db.generate_mapping(create_tables=True))

@orm.db_session
def test():
    #r = M.Account.get(AccountName="Chenwe_i_lin")
    #c = M.Character(
    #    PlayerId=OfflinePlayerUUID("Chenwe_i_lin"),
    #    PlayerName="Chenwe_i_lin",
    #    Owner=r
    #)
    #c = M.Character.get(Id="2aecd12fdf1a4d7288dbbc9ca359a3f4")
    #orm.commit()
    #print(c.FormatCharacter(unsigned=False, auto=True, Properties=True))
    a1_salt = bcrypt.gensalt()
    a2_salt = bcrypt.gensalt()
    a3_salt = bcrypt.gensalt()

    a1 = M.Account(Email="test1@to2mbn.org",
                   AccountName="test1",
                   Password=bcrypt.hashpw("111111".encode(), a1_salt),
                   Salt=a1_salt)
    a2 = M.Account(Email="test2@to2mbn.org",
                   AccountName="test2",
                   Password=bcrypt.hashpw("222222".encode(), a2_salt),
                   Salt=a2_salt)
    a3 = M.Account(Email="test3@to2mbn.org",
                   AccountName="test3",
                   Password=bcrypt.hashpw("333333".encode(), a3_salt),
                   Salt=a3_salt)

    r1 = M.Resource(
        PicHash=
        "81c26f889ba6ed12f97efbac639802812c687b4ffcc88ea75d6a8d077328b3bf",
        Name="r1",
        PicHeight=32,
        PicWidth=64,
        Model='steve',
        Type="skin",
        Owner=a2)
    r2 = M.Resource(
        PicHash=
        "8e364d6d4886a76623062feed4690c67a23a66c5d84f126bd895b903ea26dbee",
        Name="r2",
        PicHeight=32,
        PicWidth=64,
        Model='none',
        Type='cape',
        Owner=a2)
    r3 = M.Resource(
        PicHash=
        "490bd08f1cc7fce67f2e7acb877e5859d1605f4ffb0893b07607deae5e05becc",
        Name="r3",
        PicHeight=32,
        PicWidth=64,
        Model='alex',
        Type='skin',
        Owner=a3)
    r4 = M.Resource(
        PicHash=
        "ddcf7d09723e799e59d7f19807d0bf5e3a2c044ce17e76a48b8ac4d27c0b16e0",
        Name="r3",
        PicHeight=32,
        PicWidth=64,
        Model='none',
        Type='cape',
        Owner=a3)

    c1 = M.Character(PlayerId=OfflinePlayerUUID("character1"),
                     PlayerName="character1",
                     Owner=a2,
                     Skin=r1,
                     Cape=r2)
    c2 = M.Character(PlayerId=OfflinePlayerUUID("character2"),
                     PlayerName="character2",
                     Owner=a3,
                     Skin=r3)
    c3 = M.Character(PlayerId=OfflinePlayerUUID("character3"),
                     PlayerName="character3",
                     Owner=a3,
                     Cape=r4)
    # orm.TransactionIntegrityError
    # unique错误会爆pony.orm.core.TransactionIntegrityError
    orm.commit()

    cache_pool.close_scavenger()

test()
#cProfile.run("test()")
#cProfile.run("asyncio.run(test())")