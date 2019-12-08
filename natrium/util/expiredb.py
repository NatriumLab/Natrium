from threading import Thread
import asyncio
import atexit
import uvicorn
import random
import maya
from functools import reduce
import threading
from .inf import INFINITY
import signal
import sys
import blinker
from .randoms import String
import math
import time
import datetime

class AioExpireDB():
    """通过threading.Thread运行独立的事件循环来保证其他协程的持续运行.\n
    因为atexit似乎对uvicorn没用,所以需要传入fastapi的app来获取event.
    """
    _ExitSignal = False
    local_loop = None
    scavenger_thread = None
    Body = {}
    Expire_Datas = {}
    lock = threading.RLock()

    def isExpired(self, key):
        """过期返回True, 没有返回False"""
        if key not in self.Expire_Datas:
            raise ValueError(f"{key} has not setted.")
        if self.Expire_Datas[key]["date"] is INFINITY:
            return False
        return self.Expire_Datas[key]["date"] < maya.now()

    def event_shutdown_listener(self):
        self._ExitSignal = True
        self.Body.clear()
        self.Expire_Datas.clear()

    async def scavenger(self):
        while not self._ExitSignal:
            await asyncio.sleep(1)
            #print(len(self.Body), end=" ")
            #sys.stdout.flush()
            
            data_num = len(self.getlib())
            if data_num == 0:
                continue
            original_keys = list(self.getlib().keys())
            with self.lock:
                result = random.choices(range(len(self.Expire_Datas)), k=math.ceil(data_num / 20))
                result = reduce(lambda x, y:x if y in x else x + [y], [[], ] + result)
                # 特殊的按顺序去重
                if result:
                    print(data_num, [i for i in result if i > data_num])
                    for i in [i for i in result if i < data_num]:
                        key = original_keys[i]
                        if self.isExpired(key):
                            self.delete(key)

    def count(self):
        with self.lock:
            return len(self.Body)

    def count_expire_datas(self):
        with self.lock:
            return len(self.Expire_Datas)

    def delete(self, key):
        with self.lock:
            del self.Expire_Datas[key]
            del self.Body[key]

    def get(self, key, default=None):
        try:
            if self.isExpired(key): # 如果在但是过期了
                self.delete(key)
                return
        except ValueError: # 不在
            return default
        return self.Body[key]

    def __getitem__(self, item):
        r = String()
        result = self.get(item, r)
        if result == r:
            raise KeyError(item)
        return result

    def getlib(self):
        with self.lock:
            return self.Body.copy()

    def __setitem__(self, item, value):
        self.set(item, value)
    
    def __delitem__(self, item):
        self.delete(item)

    def set(self, key, value, date=INFINITY):
        """可指定日期, 到时key无效."""
        with self.lock:
            self.Body[key] = value
            self.Expire_Datas[key] = {"date": date}

    def setByTimedelta(self, key, value, delta={}):
        """通过timedelta实现日期偏移计算
        """
        with self.lock:
            offset = datetime.timedelta(**delta)
            if offset.total_seconds() == 0:
                self.set(key, value)
            else:
                self.set(key, value, maya.now() + offset)

    def keys(self):
        return self.Body.keys()

    def has(self, key):
        r = String()
        return self.get(key, r) != r

    def __next__(self):
        yield from self.Body.keys()

    def __init__(self, app):
        self.local_loop = asyncio.new_event_loop()
        def loop_runfunc(loop, coro):
            asyncio.set_event_loop(loop)
            print(loop.run_until_complete(coro))

        self.scavenger_thread = Thread(target=loop_runfunc,args=(self.local_loop, self.scavenger()))
        self.scavenger_thread.start()
        self.lock = threading.RLock()

        # 监听服务关闭事件, 如果不监听则需要强制关闭
        app.on_event("shutdown")(self.event_shutdown_listener)