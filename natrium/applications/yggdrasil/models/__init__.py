from conf import config
import uuid
import maya
from natrium.applications.yggdrasil import auth_token_pool
from typing import Optional, List

class Token(object):
    Account = None
    Character = None

    ValidateDate = None
    AvailabilityDisableDate = None

    AccessToken = None
    ClientToken = None

    def __init__(self, Account, Character=None, ClientToken=None,):
        self.AccessToken = uuid.uuid4()
        if ClientToken:
            self.ClientToken = ClientToken
        else:
            self.ClientToken = uuid.uuid4().hex

        self.Account = Account
        self.Character = Character

        self.ValidateDate = maya.now().add(**config['token']['validate']['maya-configure'])
        self.AvailabilityDisableDate = maya.now().add(**config['token']['availability']['maya-configure'])

    def setupCharacter(self, Character) -> bool:
        if not self.Character:
            self.Character = Character
            return True
        else:
            return False

    @staticmethod
    def getToken(AccessToken: str, ClientToken: Optional[str] = None):
        r = auth_token_pool.get(uuid.UUID(AccessToken))
        if not r:
            return None
        if ClientToken:
            if r.ClientToken != ClientToken: # 如果不匹配, 则爆炸
                return None
        return r

    @property
    def is_disabled(self) -> bool:
        return self.ValidateDate < maya.now()

    @property
    def is_alived(self) -> bool:
        """该接口表示Token是否可以正常使用"""
        return self.AvailabilityDisableDate > maya.now()

    @staticmethod
    def getManyTokens(user):
        cloned = auth_token_pool.getlib()
        return [i for i in cloned.values() if i.Account.Id == user.Id]
