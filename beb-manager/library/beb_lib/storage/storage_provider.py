from collections import namedtuple
from peewee import SqliteDatabase
from beb_lib import (IProviderSubscriber,
                     IProvider,
                     BaseError)
from .storage_provider_protocol import IStorageProviderProtocol
from .storage_models import (Board,
                             CardList,
                             Tag,
                             Card,
                             TagCard,
                             CardUserAccess,
                             CardListUserAccess,
                             BoardUserAccess,
                             Comment,
                             DATABASE_PROXY)


class StorageProvider(IProvider, IStorageProviderProtocol):
    """
    Designed to create a kind of interlayer between the core and concrete DB implementation
    """

    def __init__(self, path_to_db: str):
        self.database_path = path_to_db
        self.database = SqliteDatabase(path_to_db)
        self.is_connected = False
        DATABASE_PROXY.initialize(self.database)

    def open(self) -> None:
        if not self.is_connected:
            self.database.connect()
            self.is_connected = True
        self.database.create_tables([Board,
                                     CardList,
                                     Tag,
                                     Card,
                                     TagCard,
                                     CardUserAccess,
                                     CardListUserAccess,
                                     BoardUserAccess,
                                     Comment])

    def close(self) -> None:
        self.database.close()

    def execute(self, request: namedtuple, subscriber: IProviderSubscriber = None) -> None:
        pass

    def sync_execute(self, request: namedtuple) -> (namedtuple, BaseError):
        pass
