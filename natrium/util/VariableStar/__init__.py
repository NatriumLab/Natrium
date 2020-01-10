try:
    import orjson
except ModuleNotFoundError:
    pass
else:
    from .orjson_support import OrjsonResponse