import natrium.database.models as M
from typing import Optional, List, Dict
from uuid import UUID
import uuid
from natrium.util.randoms import String
import maya
from conf import config
from datetime import timedelta
from natrium.util.objective_dict import ObjectiveDict
from natrium.util.passwd import verify_passwd

config = ObjectiveDict(config)

class Token:
    AccessToken: Optional[UUID] = None
    ClientToken: Optional[UUID] = None
    
    Account: Optional[M.Account] = None

    AliveDate: Optional[maya.MayaDT] = None
    ExpireDate: Optional[maya.MayaDT] = None

    Danger: bool = False

    def __init__(self, Account: M.Account, ClientToken: Optional[str] = None):
        self.AccessToken = uuid.uuid4()
        self.ClientToken = ClientToken or String(16)

        self.Account = Account
        
        self.AliveDate = maya.now() + timedelta(**config.natrium.token.alive).total_seconds()
        self.ExpireDate = maya.now() + timedelta(**config.natrium.token.expire).total_seconds()

    def transferToDangerous(self, password: str):
        if verify_passwd(password, self.Account.Password):
            self.Danger = True

    @property
    def is_expired(self):
        return self.ExpireDate < maya.now()

    @property
    def is_alive(self):
        return self.AliveDate > maya.now()

    def __enter__(self):
        """用上下文管理器, 对外界暴露一系列可被规范的接口, 相当于废案中的Ship"""
        class wrapper:
            events = {
                "alive": self.is_alive,
                "disabled": self.is_expired,
                "refreshable": (lambda: not self.is_expired and not self.is_expired)(),
                "be_dangerous": self.Danger
            }
            results = {}
            extends = ObjectiveDict(
                Account=self.Account,
                TokenObj=self,
            )

            def on(self, method_name, args=[], kwargs={}):
                def w(fn):
                    assert method_name in self.events
                    if self.events[method_name]:
                        self.results[fn.__name__] = fn(*args, **kwargs)
                    return fn
                return w

            def getResult(self, name):
                return self.results[name]
        return wrapper()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass