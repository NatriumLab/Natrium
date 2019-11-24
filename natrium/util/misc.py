class NonReturnCallable:
    def __init__(self):
        pass

    def __call__(self):
        pass

class AlwaysTrueCallable:
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        return True