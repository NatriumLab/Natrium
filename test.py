from pymongo import MongoClient, InsertOne
from conf import config

ConnectInfo = config['connection']['mongo']

AliveConnection = MongoClient(
    host=ConnectInfo['host'],
    port=ConnectInfo['port'],
    username=ConnectInfo['auth']['username'],
    password=ConnectInfo['auth']['password'],

    connect=True
)
faq = {'y': 1}

print(AliveConnection['natrium']['cc'].bulk_write([InsertOne(faq)]).upserted_ids)
print(faq)