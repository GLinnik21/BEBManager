import random
from collections import namedtuple
from threading import Lock

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
        self.mutex = Lock()

    def add_user(self, name):
        request = UserDataRequest(request_id=random.random(), id=None, name=name, request_type=RequestType.WRITE)
        self.mutex.acquire(blocking=False)
        self.user_provider.execute(request, self)
        self.mutex.acquire(blocking=True)

    def process(self, respond: namedtuple, error: namedtuple = None) -> None:
        self.mutex.release()
