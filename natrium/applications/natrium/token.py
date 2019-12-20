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
from .buckets import TokenBucket

config = ObjectiveDict(config)

class Token:
    AccessToken: Optional[UUID] = None
    ClientToken: Optional[str] = None
    
    Account: Optional[M.Account] = None

    CreateAt: Optional[maya.MayaDT] = None
    AliveDate: Optional[maya.MayaDT] = None
    ExpireDate: Optional[maya.MayaDT] = None

    Danger: bool = False

    def __init__(self, Account: M.Account, ClientToken: Optional[str] = None):
        self.AccessToken = uuid.uuid4()
        self.ClientToken = ClientToken or String(16)

        self.Account = Account
        
        self.CreateAt = maya.now()
        self.AliveDate = maya.now() + timedelta(**config.natrium['token']['alive'])
        self.ExpireDate = maya.now() + timedelta(**config.natrium['token']['expire'])

    def transferToDangerous(self, password: str):
        if verify_passwd(password, self.Account.Password):
            self.Danger = True

    @staticmethod
    def getToken(AccessToken: str, ClientToken: Optional[str] = None) -> "Token":
        r = TokenBucket.get(uuid.UUID(AccessToken))
        if not r:
            return None
        if ClientToken:
            if r.ClientToken != ClientToken: # 如果不匹配, 则爆炸
                return None
        return r

    @property
    def is_expired(self):
        return self.ExpireDate < maya.now()

    @property
    def is_alive(self):
        return self.AliveDate > maya.now()