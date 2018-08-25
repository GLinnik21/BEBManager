import random
from collections import namedtuple

from application import config
from beb_lib import (StorageProvider,
                     IProviderSubscriber,
                     RequestType,
                     Model)
from storage import (UserProvider,
                     UserDataRequest,
                     UserInstance)


class App(IProviderSubscriber):

    def __init__(self):
        self.lib_model = Model(StorageProvider(config.LIB_DATABASE))
        self.user_provider = UserProvider(config.APP_DATABASE)
        self.user_provider.open()

    def add_user(self, name: str) -> None:
        request = UserDataRequest(request_id=random.randrange(1000000),
                                  id=None,
                                  name=name,
                                  request_type=RequestType.READ)
        result = self.user_provider.sync_execute(request)

        if result[0] is not None:
            print("This username have been already taken!")
            quit()

        request = UserDataRequest(request_id=random.randrange(1000000),
                                  id=None,
                                  name=name,
                                  request_type=RequestType.WRITE)
        result = self.user_provider.sync_execute(request)

        if result[1] is not None:
            print(result[1].description)
            quit()

    def get_user_by_id(self, user_id: int) -> UserInstance:
        request = UserDataRequest(request_id=random.randrange(1000000),
                                  id=user_id,
                                  name=None,
                                  request_type=RequestType.READ)
        result = self.user_provider.sync_execute(request)
        return result[0]

    def process(self, respond: namedtuple, error: namedtuple = None) -> None:
        pass
