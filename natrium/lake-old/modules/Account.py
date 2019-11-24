from ..models.account import Account
from natrium.lake import Lake
from pymongo import IndexModel, ASCENDING, DESCENDING
from .Line import LineLake
from typing import Optional
from ..register import REGISTER_DICT
from .Line import LineLake

class AccountLake(Lake):
    Indexes = [
        IndexModel([("id", ASCENDING)], unique=True),
        IndexModel([("email", ASCENDING)], unique=True)
    ]
    CollectionName = "Account"
    Prototype = Account
    RequireLake = [LineLake]

    async def CreateAccountByMessage(self, message):
        return await self.SaveObject(self.Prototype.CreateFromFormat(message).format())

    async def Signout(self, Account: Account):
        Ob_LineLake: LineLake = REGISTER_DICT["Line"]
        Lines = Ob_LineLake.QueryAccountLines(Account.Id)
        return [await Ob_LineLake.RemoveLine(i.AccessToken, i.ClientToken)\
             for i in Lines]

    async def Authenticate(self, RawPass=None, Email=None, Account: Optional[Account] = None):
        if not any([Email, Account]):
            return
        if not RawPass:
            return

        if not Account and isinstance(Account, self.Prototype):
            return
        if Email:
            Account = await self.SelectedCollection.find_one({"email": Email})

        if not Account.PasswordVerify(RawPass):
            return
        Ob_LineLake: LineLake = REGISTER_DICT["Line"]
        return Ob_LineLake.CreateMasterByObject(Account)