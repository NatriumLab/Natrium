from typing import Any, Dict
from ..util.misc import NonReturnCallable, AlwaysTrueCallable

class Field:
    _value: Any = None
    Optional: bool = False # 决定是否会调用default

    def __init__(self):
        pass

    default = NonReturnCallable()
    verify = AlwaysTrueCallable()

    def translate(self, value) -> Any:
        """
        将值(可以在mongo数据库中存储的基本类型)转换为py_value
        """
        return value

    def render(self, value) -> Dict:
        """
        将值转换为可以在mongo数据库中存储的基本类型
        """
        return dict(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value_setter(self, value):
        if self.verify(value):
            self._value = value
        else:
            raise ValueError(f"verify error: {value}")

    