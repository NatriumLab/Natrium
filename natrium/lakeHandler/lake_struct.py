from typing import Optional, Any
from ..util.pave import pave
from pymongo import UpdateOne, InsertOne
from ..util.objective_dict import BuiltinInterface

def print_and_return(v):
    print(v)
    return v

class Struct:
    parent_lake: Optional[Any] = None
    original_struct_dict = {}
    struct_dict = {}
    mongo_id = None

    def __getattr__(self, attrname):
        """
        暂且用的通用方式, 若有问题以后再改.
        另: 现在仍然是直接改字典.
        """
        if not attrname.startswith("__") and attrname.endswith("__"):
            return getattr(self, attrname)
        else:
            if attrname == "builtin": # 用于访问内部方法
                return BuiltinInterface(self)
            return self.struct_dict[attrname]

    def __setattr__(self, name, value):
        """
        直接改字典.
        """
        if not name.startswith("__") and name.endswith("__"):
            setattr(self, name, value)
        else:
            if name == "builtin":
                raise KeyError("builtin is used to access these built-in method and attr, so you cannot set this attr.")
            if name not in self.parent_lake.fields:
                raise KeyError(f'"{name}" does not be in the lake: "{self.parent_lake.__name__}"')
            if not self.parent_lake.fields[name].verify(value):
                raise ValueError(f'value "{value}" should be commitable in verify.')
            self.struct_dict[name] = value

    def __init__(self, parent_lake, struct_dict, _id=None, is_create=False):
        """
        需要传入lake实例(用于调用save和规范field)\n
        struct_dict是一个field的dict(key就是field name, value会给verify过一遍)\n
        另外,因为我认为这里一般是在translate过程中汇聚键值,所以没!有!用!translate\n
        在lake的创建过程中,会阻止一些特殊的field_name(比如说builtin, 这个关键字被用于访问Struct的内部方法)
        """
        if _id and not is_create:
            self.mongo_id = _id
        else:
            if not is_create:
                self.mongo_id = struct_dict.get("_id")
            else:
                self.mongo_id = None
        self.parent_lake = parent_lake
        self.struct_dict = {i.__name__: struct_dict.copy()[i.__name__] for i in parent_lake.fields.keys()}
        self.original_struct_dict = {i.__name__: struct_dict.copy()[i.__name__] for i in parent_lake.fields.keys()}
        # 对以后的傻逼的我说no...

    def update_by_dict(self, another_dict):
        # 防止我update一些奇怪的key.
        self.struct_dict.update({i.__name__: another_dict[i.__name__] for i in self.parent_lake.fields.keys() if i.__name__ in another_dict})

    def update_by_kwargs(self, **kwargs):
        self.struct_dict.update({i.__name__: kwargs[i.__name__] for i in self.parent_lake.fields.keys() if i.__name__ in kwargs})

    def diff_with_original(self):
        return {k: v for k, v in pave(self.struct_dict).items() if pave(self.original_struct_dict).get(k) != v}

    async def save(self):
        # 防止我以后傻逼的放一些奇妙的key进去, 先安排上...
        # 不要问我为什么需要async, 因为我们基于asyncio(motor).
        # 吐槽下, type hint对于motor没用了, 识别成str类型, 醉了
        structived = {
            i.__name__:self.struct_dict[i.__name__]
            for i in self.parent_lake.fields.keys()
        } # 即只有lake里定义的字段的字典
        
        require_update = {
            k: v for k, v in pave(structived).items()
            if pave(self.original_struct_dict).get(k) != v
        }
        if self.mongo_id: # 表明这是一次更新动作
            result = await self.parent_lake.bulk_write(UpdateOne({"_id": self.mongo_id}, require_update))
        else: # 一次插入动作
            result = await self.parent_lake.bulk_write(InsertOne(structived))
            self.mongo_id = structived['_id']
        return result