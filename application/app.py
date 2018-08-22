import random
from collections.__init__ import namedtuple
from typing import Any

from application import config
from beb_lib import (StorageProvider,
                     IProviderSubscriber,
                     RequestType,
                     Model)
from .storage import (UserProvider,
                      UserDataRequest)


class App(IProviderSubscriber):

    def __init__(self):
        self.lib_model = Model(StorageProvider(config.LIB_DATABASE))
        self.user_provider = UserProvider(config.APP_DATABASE)
        self.user_provider.open()

    def add_user(self, name):
        request = UserDataRequest(request_id=random.random(), id=None, name=name, request_type=RequestType.WRITE)
        self.user_provider.execute(request, self)

    def process(self, respond: Any, error: namedtuple = None) -> None:
        pass
