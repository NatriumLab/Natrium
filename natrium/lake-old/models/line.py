
from dataclasses import dataclass
from typing import Dict, List, AnyStr, Optional, Callable, Generic, Any, Union
import maya
from conf import config
from uuid import UUID
import uuid
#from .exceptions import *
from ..exceptions import PropertyException, NonExceptFollowingException, NonForkableException, TokenValidatedException 
from natrium.util import randoms
import datetime
from .account import Account

@dataclass(init=False, repr=True, eq=True)
class Line(object):
    """以树型结构管理用户的令牌"""

    AccessToken: UUID
    ClientToken: UUID

    is_master: bool

    @property
    def is_validated(self):
        return self.ValidateDate < maya.now()

    @property
    def is_usable(self):
        return self.AvailabilityDisableDate > maya.now()

    parent: Optional[str]
    _require: List[Optional[str]]

    @property
    def require(self):
        return self._require

    def _depth_checker(self):
        if not (len(self._require) + 1) <= config['tree']['depth']:
            raise ValueError(f"Depth cannot exceed {config['tree']['depth']}")

    Account: Optional = None
    Character: Optional = None

    ValidateDate: Optional[maya.MayaDT] = None
    AvailabilityDisableDate: Optional[maya.MayaDT] = None

    branch: Optional[str] = None # 取祖父(Master)
    commit_date: Optional[maya.MayaDT] = None
    commit_id: Optional[str] = None

    following_group: Optional[uuid.UUID] = None

    forkable: Optional[bool] = False
    disposable: Optional[bool] = False # 一次性使用
    dangerous: Optional[bool] = False # 是否可以执行危险操作

    def __init__(self, *args, **kwargs):
        pass

    async def fork(self, forkable=False, disposable=False):
        if not self.forkable:
            raise NonForkableException(f"{self.AccessToken} has been non-forkable.")

        if self.is_validated:
            raise TokenValidatedException(f"{self.AccessToken} has validated.")

        if len(self._require) >= config['tree']['depth']:
            raise ValueError(f"{self.AccessToken} has forked {config['tree']['depth']}")

        FactoryResult = self.__class__()
        FactoryResult.AccessToken = uuid.uuid4()
        FactoryResult.ClientToken = self.ClientToken
        FactoryResult.is_master = False
        FactoryResult.parent = self.AccessToken
        self._depth_checker()
        FactoryResult._require = self._require + [self.AccessToken]
        FactoryResult.Account=self.Account
        FactoryResult.ValidateDate = maya.now().add(**config['token']['validate']['maya-configure'])
        FactoryResult.AvailabilityDisableDate = maya.now().add(**config['token']['availability']['maya-configure'])
        FactoryResult.branch = self.AccessToken
        FactoryResult.commit_date = maya.now()
        FactoryResult.commit_id = randoms.String()
        FactoryResult.following_group = self.following_group
        FactoryResult.forkable = forkable
        FactoryResult.disposable = disposable

        return FactoryResult

    @classmethod
    async def Create(cls, account: Account, master=False, forkable=False, following=None, group=None, ClientToken=None):
        if master and following:
            raise NonExceptFollowingException("master branch cannot follow another line.")

        if master and not forkable:
            raise PropertyException("master branch must be forkable.")

        FactoryResult = cls()

        FactoryResult.AccessToken = uuid.uuid4()
        if not ClientToken:
            FactoryResult.ClientToken = uuid.uuid4()
        else:
            FactoryResult.ClientToken = ClientToken
        FactoryResult.is_master = master
        FactoryResult.parent = None
        FactoryResult._require = []
        FactoryResult.Account=account.Id
        FactoryResult.ValidateDate = maya.now().add(**config['token']['validate']['maya-configure'])
        FactoryResult.AvailabilityDisableDate = maya.now().add(**config['token']['availability']['maya-configure'])
        FactoryResult.branch = "master" if master else following
        FactoryResult.commit_date = maya.now()
        FactoryResult.commit_id = randoms.String()
        FactoryResult.following_group = group
        FactoryResult.forkable = master or forkable

        return FactoryResult

    def format(self):
        return {
            "key": {
                "accessToken": self.AccessToken,
                "clientToken": self.ClientToken
            },
            "is_master": self.is_master,
            "parent": self.parent,
            "require": self._require,
            "bind": {
                "account": self.Account.Id,
                "character": self.Character,
                "group": self.following_group
            },
            "times": {
                "validate": self.ValidateDate.datetime(),
                "availability": self.AvailabilityDisableDate.datetime()
            },
            "metas": {
                "branch": self.branch,
                "commit_date": self.commit_date.datetime(),
                "commit_id": self.commit_id,
                "able_to": {
                    "fork": self.forkable,
                    "disposable": self.disposable,
                    "danger": self.dangerous
                }
            }
        }

    @classmethod
    async def createFromFormat(cls, message):
        FactoryResult = cls()

        FactoryResult.AccessToken = message['key']['accessToken']
        FactoryResult.ClientToken = message['key']['clientToken']
        FactoryResult.is_master = message['is_master']
        FactoryResult.parent = message['parent']
        FactoryResult._require = message['require']
        FactoryResult.Account = message['bind']['account']
        FactoryResult.Character = message['bind']['character']
        FactoryResult.ValidateDate = maya.MayaDT(message['times']['validate'].timestamp())
        FactoryResult.AvailabilityDisableDate = maya.MayaDT(message['times']['availability'].timestamp())
        FactoryResult.branch = message['metas']['branch']
        FactoryResult.commit_date = message['metas']['commit_id']
        FactoryResult.following_group = message['bind']['group']
        FactoryResult.forkable = message['metas']['able_to']['fork']
        FactoryResult.disposable = message['metas']['able_to']['disposable']
        FactoryResult.dangerous = message['metas']['able_to']['danger']

        return FactoryResult

    def UpdateQueryMsg(self):
        return {
            "key.accessToken": self.AccessToken
        }