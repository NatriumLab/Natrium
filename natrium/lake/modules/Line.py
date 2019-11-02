import conf
from natrium.lake.models.line import Line
from .. import Lake
from typing import Any
import motor.motor_asyncio
from pymongo.errors import ConnectionFailure
import sys
from typing import Optional, Dict, List
from pymongo import IndexModel, DESCENDING, ASCENDING

class LineLake(Lake):
    Indexes = [
        IndexModel([("key.accessToken", ASCENDING)], unique=True),
        IndexModel([("key.clientToken", ASCENDING)]),
        IndexModel([
            ("bind.account", ASCENDING),
            ("bind.character", ASCENDING)
        ], name="binding"),
        IndexModel([
            ("times.availability", ASCENDING)
        ], expireAfterSeconds=0) # 过期索引
    ]
    CollectionName = "Line"
    Prototype = Line

    async def CreateMasterByObject(self, Account):
        return await self.Prototype.Create(Account, master=True, forkable=True)

    async def QueryLine(self, accessToken, clientToken=None)->Line:
        if not clientToken:
            DBResult = await self.SelectedCollection.find_one({
                "key.accessToken": accessToken
            })
        else:
            DBResult = await self.SelectedCollection.find_one({
                "key.accessToken": accessToken,
                "key.clientToken": clientToken
            })
        if not DBResult:
            return None
        LineResult = await self.Prototype.createFromFormat(DBResult)
        return LineResult

    async def RemoveLine(self, accessToken, clientToken=None):
        LineResult = await self.QueryLine(accessToken, clientToken)
        if LineResult.is_validated:
            await self.SelectedCollection.delete_many({
                "require": {
                    "$elemMatch": {
                        "$eq": LineResult.AccessToken
                    }
                }
            }) # 删除所有...
            return None # 这里会直接返回None

    async def QueryAccountLines(self, AccountID):
        return [i for i in [await self.Prototype.createFromFormat(i) async for i in self.SelectedCollection.find({
            "bind.account": AccountID
        })]]# if not i.is_validated

    async def ReflushLines(self, AccessToken, ClientToken=None, BindCharacter=NOne):
        Line = self.QueryLine(AccessToken, ClientToken)
        if not Line:
            return
        if Line.is_validated:
            return
        OriginalClientToken = Line.ClientToken
