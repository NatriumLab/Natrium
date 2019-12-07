def IIFE(*args, **kwargs):
    def deco(fn):
        fn(*args, **kwargs)
        return fn
    return deco

if __name__ == "__main__":
    @IIFE(key="h2")
    def world(key):
        print("{key}, world!".format(key=key))

    print(world)