import sys
from functools import singledispatch

def _smooth_handle(Id):
    # get contents
    direct = sys._getframe(1).f_locals['direct']
    target = sys._getframe(1).f_locals['target']
    parent = sys._getframe(1).f_locals['parent']

    if not isinstance(target[Id], (dict, list)):
        direct[f"{parent}.{Id}" if parent else Id] = target[Id]
    else:
        direct = dict(direct, **smooth(target[Id], parent=f"{parent}.{Id}" if parent else f"{Id}"))
    return direct

@singledispatch
def smooth(target, parent="", indirect=None):
    direct = indirect if indirect else {}
    return {k:v for d in [(indirect if indirect else {}), direct] for k,v in d.items()}

@smooth.register(dict)
def _(target, parent="", indirect=None):
    direct = indirect if indirect else {}
    for k in target:
        direct = _smooth_handle(k)
    return {k:v for d in [(indirect if indirect else {}), direct] for k,v in d.items()} 

@smooth.register(list)
def _(target, parent="", indirect=None):
    direct = indirect if indirect else {}
    for index in range(len(target)):
        direct = _smooth_handle(index)
    return {k:v for d in [(indirect if indirect else {}), direct] for k,v in d.items()} 

if __name__ == "__main__":
    print(smooth({
        "f": {
            "r": {
                "c": "v"
            },
            "c": "r",
            "u": [
                "1", 2, "34"
            ]
        }
    }))