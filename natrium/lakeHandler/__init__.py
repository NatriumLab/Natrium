import asyncio
import inspect
import re

import pymongo
from pymongo import ASCENDING, DESCENDING, IndexModel  # 引导顺序

from conf import config

from ..util.misc import NonReturnCallable
from .connection import AliveConnection, ConnectInfo
from .field import Field
from ..util.objective_dict import ObjectiveDict
from .lake_struct import Struct

class LakeMeta(type):
    def lake_create(self, **kwargs):
        result = {}
        for i in self.fields.keys(): # 遍历字段
            if i not in kwargs: # 判断一个是否在提供的参数中, 如果没有尝试取默认值:
                if not isinstance(self.fields[i].default, NonReturnCallable) and self.fields[i].Optional:
                    # 如果该字段没有default, 且Optional为True
                    raise ValueError(f"{self.__name__}.{i}: The 'default' method is required when make 'field.optional' true.")
                else:
                    result[i] = self.fields[i].default() # 取默认值并放到result里
            else:
                # i在提供的参数里
                if not self.fields[i].verify(kwargs[i]):
                    # 提供的参数不合法
                    raise ValueError(f'{self.__name__}.{i}: You have provided an illegal value: {kwargs[i]}, type: {type(kwargs[i])}')
                # 提供的参数合法
                result[i] = kwargs[i]
        return Struct(self, result, is_create=True)

    async def bluk_write(self, requests):
        return await self.connection.collection.bluk_write(requests)

    def __new__(cls, name, extends, mappings: dict):
        handled_map = ObjectiveDict({
            "fields": {},
            "indexes": {},
            "metas": {},
            "mappings": {},
            "connection": ObjectiveDict({
                "connect": AliveConnection,
                "database": AliveConnection[config['connection']['mongo']['db']],
                "collection": None
            }),

            "bluk_write": classmethod(cls.bluk_write),
            "__getitem__": classmethod(lambda self, name: self.fields[name]),
            "__name__": name
        })
        if inspect.isclass(mappings.get("fields")):
            for k, v in vars(mappings.get("fields")).items(): # Field
                if inspect.isclass(v) and not (k.startswith("__") and k.endswith("__")):
                    if Field not in v.__bases__:
                        raise TypeError("you should give a Field.")
                    if not v.Optional:
                        if not isinstance(v.default, NonReturnCallable):
                            # 如果optional = false, 且没有重载default方法
                            raise ValueError(f"{name}.{k}: The 'default' method is required when make 'field.optional' true.")
                    handled_map.fields[k] = v

        if inspect.isclass(mappings.get("indexes")):
            # key随便, value就是IndexModel
            for k, v in vars(mappings['indexes']).items():
                if not (k.startswith("__") and k.endswith("__")):
                    if not isinstance(v, IndexModel):
                        raise TypeError(f"index {k} must be a pymongo.IndexModel.")
                    handled_map.indexes[k] = v

        if inspect.isclass(mappings.get("mappings")):
            for k, v in vars(mappings.get("mappings")).items():
                if not (k.startswith("__") and k.endswith("__")):
                    # 匹配是否被注册\是否是字符串\名称是否合规
                    if not False in (
                        k in handled_map.fields, # 是否被注册
                        isinstance(v, str), # 是否为字符串
                        bool(re.match(r"^([a-zA-Z])[a-zA-Z0-9_]*$", v)) # 名称是否合规
                    ):
                        handled_map.mapping[k] = v
                    else:
                        raise ValueError(f"illegal mapping value: {v}")

            """
            # 判断是否全部被map
            if handled_map['mappings'].keys()[:] != handled_map['fields'].keys()[:]:
                raise ValueError("fields must all be mapped.")
            """
        if inspect.isclass(mappings.get("metas")):
            for k, v in vars(mappings.get("metas")).items():
                if not (k.startswith("__") and k.endswith("__")):
                    handled_map.metas[k] = v

        if handled_map.metas.get("collection"): # 选择使用的collection
            handled_map.connection.collection = handled_map.connection.database[handled_map['metas'].get("collection")]

        # 判断是否选择了collection
        if not handled_map.connection.collection:
            raise ValueError(f"you must select a standed collection: LakeName:{name}")

        # 检查field设置
        for k, v in handled_map.fields.items():
            value_dir = {lo_k: lo_v for lo_k, lo_v in vars(v).items() if not (lo_k.startswith("__") and lo_k.endswith("__"))}
            # 检查Field中各个参数是否设置正确.

            # 检查重写参数是否是non-callable
            assert_callable_list = [
                callable(i) for i in [
                    value_dir.get("default", Field.default),
                    value_dir.get("translate", Field.translate),
                    value_dir.get("render", Field.render),
                    value_dir.get("verify", Field.verify)
                ]
            ]
            assert_list = [
                "default", "translate", "render", "verify"
            ]
            if False in assert_callable_list:
                false_index_list = [i for i in range(len(assert_callable_list)) if not assert_callable_list[i]]
                raise ValueError(f"in lake '{k}' , these attr should be callable: {[assert_list[i] for i in false_index_list]}")

            # 检查是否同时设置了Optional和default方法
            if value_dir.get("Optional") and isinstance(value_dir.get("default"), NonReturnCallable):
                raise ValueError(f"in lake '{k}' , you should not make this optional and set 'default' up.")
            # 若是没有重写verify方法, 默认就是"Always True", 这表示其不需要进行值检查.

        # 连接数据库, 开始处理(使用了pymongo的同步连接)
        
        SyncConnection = pymongo.MongoClient(
            host=ConnectInfo['host'],
            port=ConnectInfo['port'],
            username=ConnectInfo['auth']['username'],
            password=ConnectInfo['auth']['password'],
    
            connect=True
        )
        sync_collection = SyncConnection[config['connection']['mongo']['db']][handled_map.connection.collection.name]
        if handled_map.indexes: # 首先注册索引
            sync_collection.drop_indexes()
            sync_collection.create_indexes(list(handled_map.indexes.values()))
            
        if handled_map.metas.get("drop_when_init"):
            sync_collection.drop()
            
        SyncConnection.close()
        return type(name, extends, handled_map)

class test(metaclass=LakeMeta):
    class fields:
        class Id(Field):
            Optional = True
            def default(self):
                return __import__("uuid").uuid4()

        class Name(Field):
            def default(self):
                return __import__("uuid").uuid4().hex

    class metas:
        collection = "test"
        drop_when_init = False

    class mappings:
        Id = "id"
        Name = "name"

    class indexes:
        pass

print(test.indexes)
