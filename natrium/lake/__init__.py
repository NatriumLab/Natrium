import conf
from .models.line import Line
from typing import Any
import motor.motor_asyncio
from pymongo.errors import ConnectionFailure
import sys
from .exceptions import *
from typing import Optional, Dict, List, Any
from pymongo import IndexModel, DESCENDING, ASCENDING
import asyncio

class Lake(object):
    Prototype: Any = None
    MongodbClient: motor.motor_asyncio.AsyncIOMotorClient
    SelectedDatabase: motor.motor_asyncio.AsyncIOMotorDatabase
    SelectedCollection: motor.motor_asyncio.AsyncIOMotorCollection
    Indexes = []
    CollectionName: str

    @classmethod
    async def Create(cls, MongodbConnection=None):
        """
        工厂函数.
        """

        FactoryResult = cls()

        MongodbConnectionConf = conf.config['connection']['mongo']
        if not MongodbConnection:
            try:
                FactoryResult.MongodbClient = motor.motor_asyncio.AsyncIOMotorClient(
                    host=MongodbConnectionConf['host'],
                    port=MongodbConnectionConf['port'],
                    username=MongodbConnectionConf['auth']['username'],
                    password=MongodbConnectionConf['auth']['password'],

                    connect=True
                )
            except ConnectionFailure:
                sys.exit(1)
        else:
            FactoryResult.MongodbClient = MongodbConnection
        return FactoryResult

    async def SelectDatabase(self, DatabaseName: str):
        self.SelectedDatabase = self.MongodbClient[DatabaseName]
        return self.SelectedDatabase

    async def SelectCollection(self, name, AutoInit=True):
        self.SelectedCollection = self.SelectedDatabase[name]
        print(self.SelectedCollection)
        if AutoInit:
            await self.Initialization()
        return self.SelectedDatabase

    async def Select(self,
        db=conf.config['connection']['mongo']['db'],
        coll=None
    ):
        if not coll:
            coll = conf.config['connection']['mongo']['collections'][self.CollectionName]
        await self.SelectDatabase(db)
        await self.SelectCollection(coll)

    async def Initialization(self):
        # 删除旧数据
        await self.SelectedCollection.delete_many({})
        await self.SelectedCollection.drop_indexes()
        # 设置引导.
        await self.SelectedCollection.create_indexes(self.Indexes)

    async def SaveObject(self, Object):
        if not self.SelectedCollection:
            raise SelectException("this lake has not selected a collection.")
        result = await self.SelectedCollection.insert_one(Object)
        return result

    async def Query(self, message):
        return [i async for i in self.SelectedCollection.find(message)]

    async def Remove(self, message):
        return await self.SelectedCollection.find_one_and_delete(message)

    async def QueryOfSomethingInList(self, ListPath, sth):
        return self.Query({
            ListPath: {
                "$elemMatch": {
                    "$eq": sth
                }
            }
        })

    async def QueryOfSomethingNotInList(self, ListPath, sth):
        return self.Query({
            ListPath: {
                "$elemMatch": {
                    "$not": {
                        "$eq": sth
                    }
                }
            }
        })

    async def QueryOfListMatch(self, ListPath, message):
        return self.Query({
            ListPath: {
                "$elemMatch": message
            }
        })

    async def UpdateWithQuery(self, query_msg, update_msg):
        """建议query_msg填拥有唯一性的字段(如"Id", "PlayerUUID"等)"""
        return await self.SelectedCollection.update_one(query_msg, update_msg)