from ..models.account import Account
from natrium.lake import Lake
from pymongo import IndexModel, ASCENDING, DESCENDING

class AccountLake(Lake):
    Indexes = [
        IndexModel([("id", ASCENDING)], unique=True),
        IndexModel([("email", ASCENDING)], unique=True)
    ]
    CollectionName = "Account"
    Prototype = Account

    async def CreateAccountByMessage(self, message):
        return await self.SaveObject(self.Prototype.CreateFromFormat(message)).format()

    async def Signout(self)