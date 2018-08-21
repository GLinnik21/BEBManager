from collections import namedtuple
from peewee import SqliteDatabase

from beb_lib import (IProvider,
                     IStorageProviderProtocol,
                     IProviderSubscriber)
from .user import (User,
                   UserInstance,
                   DATABASE_PROXY)

UserDataRequest = namedtuple('UserDataRequest', ['id', 'name', 'request_type'])


class UserProvider(IProvider, IStorageProviderProtocol):
    """
    Instance to interact with user data base that relates to application layer
    """
    def __init__(self, path_to_db):
        self.database_path = path_to_db
        self.database = SqliteDatabase(path_to_db)
        self.is_connected = False
        DATABASE_PROXY.initialize(self.database)

    def open(self) -> None:
        if not self.is_connected:
            self.database.connect()
            self.is_connected = True
        self.database.create_tables([User])

    def close(self) -> None:
        self.database.close()

    def execute(self, request: namedtuple, subscriber: IProviderSubscriber = None) -> None:
        pass
