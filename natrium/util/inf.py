INFINITY = type("Infinity", (), {
    "__gt__": classmethod(lambda self, value: value != self), # 大于
    "__ge__": classmethod(lambda self, value: True), # 大于等于

    "__eq__": classmethod(lambda self, value: value == self), # 等于
    "__ne__": classmethod(lambda self, value: value != self), # 不等于

    "__le__": classmethod(lambda self, value: value == self or False), # 小于等于
    "__lt__": classmethod(lambda self, value: False)  # 小于
})()

NEGATIVE_INF = type("NegativeInfinity", (), {
    "__lt__": classmethod(lambda self, value: value != self), # 小于
    "__le__": classmethod(lambda self, value: True), # 小于等于

    "__eq__": classmethod(lambda self, value: value == self), # 等于
    "__ne__": classmethod(lambda self, value: value != self), # 不等于

    "__ge__": classmethod(lambda self, value: value == self or False), # 大于等于
    "__gt__": classmethod(lambda self, value: False)  # 大于
})()

if __name__ == "__main__":
    print([
        NEGATIVE_INF > NEGATIVE_INF,
        NEGATIVE_INF >= NEGATIVE_INF,
        1 > NEGATIVE_INF,
        1 < NEGATIVE_INF,
        NEGATIVE_INF < NEGATIVE_INF,
        NEGATIVE_INF <= NEGATIVE_INF
    ])