class BuiltinInterface:
    obj = None

    def __init__(self, obj):
        self.obj = obj

    def __getattr__(self, name):
        return dict.__getattribute__(self.obj, name)

class ObjectiveDict(dict):
    def __getattr__(self, name: str):
        if name == "__builtin__":
            return BuiltinInterface(self)

        if (not (name.startswith("__") and name.endswith("__"))):
            return self[name]
        else:
            return getattr(self, name)