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
from typing import Optional, Dict

class AioCacheBucket():
    """通过threading.Thread运行独立的事件循环来保证其他协程的持续运行.\n
    """
    _ExitSignal = False
    local_loop = None
    scavenger_thread = None
    Body: Optional[Dict] = None
    Expire_Datas = None
    lock = None
    default_expire_delta: Optional[Dict] = {}

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
        self.local_loop.stop()

    async def scavenger(self):
        while not self._ExitSignal:
            await asyncio.sleep(1)
            #print(len(self.Body), end=" ")
            #sys.stdout.flush()
            
            data_num = len(await self.getlib())
            if data_num == 0:
                continue
            original_keys = list((await self.getlib()).keys())
            with self.lock:
                result = random.choices(range(len(self.Expire_Datas)), k=math.ceil(data_num / 20))
                result = reduce(lambda x, y:x if y in x else x + [y], [[], ] + result)
                # 特殊的按顺序去重
                if result:
                    print(data_num, [i for i in result if i > data_num])
                    for i in [i for i in result if i < data_num]:
                        key = original_keys[i]
                        if self.isExpired(key):
                            del self.Expire_Datas[key]
                            del self.Body[key]

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

    def delete_nowait(self, key):
        del self.Expire_Datas[key]
        del self.Body[key]

    def get(self, key, default=None):
        try:
            if self.isExpired(key): # 如果在但是过期了
                self.delete(key)
                return default
        except ValueError: # 不在
            return default
        with self.lock:
            return self.Body[key]

    def getlib(self):
        with self.lock:
            return self.Body.copy()

    def set(self, key, value, date=INFINITY):
        """可指定日期, 到时key无效."""
        with self.lock:
            self.Body[key] = value
            self.Expire_Datas[key] = {"date": date}

    def setByTimedelta(self, key, value, delta={}):
        """通过timedelta实现日期偏移计算"""
        with self.lock:
            if not delta and self.default_expire_delta:
                delta = self.default_expire_delta
            offset = datetime.timedelta(**delta)
            if offset.total_seconds() == 0:
                self.set(key, value)
            else:
                self.set(key, value, maya.now() + offset)

    def keys(self):
        return self.Body.keys()

    async def has(self, key):
        r = String()
        return (self.get(key, r)) != r

    def __next__(self):
        yield from self.Body.keys()

    def __init__(self, app, scavenger=True, default_expire_delta={}, lock=None, listen_shutdown=True):
        if scavenger:
            self.local_loop = asyncio.new_event_loop()
            def loop_runfunc(loop, coro):
                asyncio.set_event_loop(loop)
                loop.run_until_complete(coro)

            self.scavenger_thread = Thread(target=loop_runfunc, args=(self.local_loop, self.scavenger()))
            self.scavenger_thread.start()

        self.default_expire_delta = default_expire_delta

        # 设置锁
        self.lock = lock or threading.RLock()

        self.Body = {}
        self.Expire_Datas = {}

        # 监听服务关闭事件, 如果不监听则需要强制关闭
        if listen_shutdown:
            app.on_event("shutdown")(self.event_shutdown_listener)

class AioMultiCacheBucket:
    BucketsLocks: Dict[str, asyncio.Lock] = {}
    Buckets: Dict[str, AioCacheBucket] = {}
    LocalLoop = None
    ScavengerLocks: Optional[Dict[str, threading.Lock]]
    ScavengerQueue = None
    ScavengerExitSignal = False
    ScavengerThread = None

    def event_shutdown_listener(self):
        self.ScavengerExitSignal = True
        self.LocalLoop.stop()

    async def scavenger_producer(self):
        while not self.ScavengerExitSignal:
            await asyncio.sleep(1)
            choiced_bucket = None
            choiced_key = None
            lock = None
            lockable = False
            while not lockable:
                if self.ScavengerExitSignal:
                    return

                if not list(self.Buckets.keys()):
                    continue

                choiced_key = random.choice(list(self.Buckets.keys()))
                lock = self.ScavengerLocks[choiced_key]
                if not self.Buckets[choiced_key].Expire_Datas: # 跳过无KEY档案
                    continue

                if not lock.locked(): # 如果没有锁住, 则跳出循环并开始清理.
                    lockable = True
                    choiced_bucket = self.Buckets[choiced_key]
                    break

            async with lock:
                bucket_lib: dict = choiced_bucket.getlib()
                lib_num = len(bucket_lib)
                lib_keys = list(bucket_lib.keys())
                result = random.choices(range(len(choiced_bucket.Expire_Datas)), k=math.ceil(lib_num / 20))
                result = reduce(lambda x, y:x if y in x else x + [y], [[], ] + result)
                #print([i for i in result if choiced_bucket.isExpired(lib_keys[i])])
                if result:
                    #print(choiced_key, lib_num, [i for i in result if i > lib_num])
                    for i in [i for i in result if i < lib_num]:
                        key = lib_keys[i]
                        if choiced_bucket.isExpired(key):
                            with self.BucketsLocks[choiced_key]:
                                choiced_bucket.delete(key)

    def __init__(self, app, buckets_options: dict, queueMaxsize=30):
        # 创建事件循环
        self.LocalLoop = asyncio.new_event_loop()
        self.RequireApp = app
        self.ScavengerLocks = {}

        for key, value in buckets_options.items():
            # 开始根据options创建初始Buckets
            result = {
                "default_expire_delta": value.get("default_expire_delta", {})
            }
            self.ScavengerLocks[key] = asyncio.Lock()
            self.BucketsLocks[key] = threading.RLock()
            self.Buckets[key] = AioCacheBucket(self.RequireApp, **result, scavenger=False, lock=self.BucketsLocks[key], listen_shutdown=False)
        
        # 构建清道夫
        def loop_runfunc(loop, tasks):
            asyncio.set_event_loop(loop)
            async def run_coro():
                return await asyncio.wait(sum(tasks, []), loop=loop)
            loop.run_until_complete(run_coro())
        
        self.ScavengerThread = Thread(target=loop_runfunc, args=(self.LocalLoop, [
            [self.scavenger_producer() for i in range(3)]
        ]))
        self.ScavengerThread.start()

        app.on_event("shutdown")(self.event_shutdown_listener)

    def setup(self, buckets_options: dict):
        for key, value in buckets_options.items():
            # 根据options创建初始Buckets
            result = {
                "default_expire_delta": value.get("default_expire_delta", {})
            }
            self.ScavengerLocks[key] = asyncio.Lock()
            self.BucketsLocks[key] = threading.RLock()
            self.Buckets[key] = AioCacheBucket(self.RequireApp, **result, scavenger=False, lock=self.BucketsLocks[key])

    def getBucket(self, bucket_name):
        return self.Buckets.get(bucket_name)