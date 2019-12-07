import natrium.database.models as M
from natrium.database.connection import db
from pony import orm
from natrium.util.hashing import OfflinePlayerUUID
from uuid import UUID
import cProfile
import asyncio

db.generate_mapping(create_tables=True)
print(M.Account.Avatar)
@orm.db_session
def test():
    r = M.Account.get(AccountName="Chenwe_i_lin")
    #c = M.Character(
    #    PlayerId=OfflinePlayerUUID("Chenwe_i_lin"),
    #    PlayerName="Chenwe_i_lin",
    #    Owner=r
    #)
    c = M.Character.get(Id="2aecd12fdf1a4d7288dbbc9ca359a3f4")
    #orm.commit()
    print(c.FormatCharacter(unsigned=False, auto=True, Properties=True))
    """
    a1 = M.Account(
        Email="1846913566@qq.com",
        AccountName="Chenwe_i_lin",
        Password="111111",
    )
    # orm.TransactionIntegrityError
    # unique错误会爆pony.orm.core.TransactionIntegrityError
    orm.commit()
    """
cProfile.run("test()")
#cProfile.run("asyncio.run(test())")