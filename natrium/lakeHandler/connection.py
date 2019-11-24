from conf import config
from motor.motor_asyncio import AsyncIOMotorClient
from ..util.inf import INFINITY
import pymongo

ConnectInfo = config['connection']['mongo']

AliveConnection = AsyncIOMotorClient(
        host=ConnectInfo['host'],
        port=ConnectInfo['port'],
        username=ConnectInfo['auth']['username'],
        password=ConnectInfo['auth']['password'],

        connect=True
    )