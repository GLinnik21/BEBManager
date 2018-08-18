from collections.__init__ import namedtuple
from typing import Any

import application.config as config
from beb_lib import (StorageProvider,
                     IProviderSubscriber,
                     RequestType,
                     Model,
                     UserDataRequest)


class App(IProviderSubscriber):

    def __init__(self):
        self.model = Model(StorageProvider(config.DATABASE))

    def add_user(self, name):
        request = UserDataRequest(id=None, name=name, request_type=RequestType.WRITE)
        self.model.execute(request, self)

    def process(self, respond: Any, error: namedtuple = None) -> None:
        pass
