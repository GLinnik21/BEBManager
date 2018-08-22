from collections import namedtuple
from peewee import SqliteDatabase, DoesNotExist

from beb_lib import (IProvider,
                     IStorageProviderProtocol,
                     IProviderSubscriber,
                     RequestType,
                     REQUEST_BASE_FIELDS)
from .user import (User,
                   UserInstance,
                   create_user_from_orm,
                   DATABASE_PROXY)

UserDataRequest = namedtuple('UserDataRequest', REQUEST_BASE_FIELDS + ['id', 'name'])


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
        if request.request_type == RequestType.WRITE:
            user = User.create(id=request.id, username=request.name)
            if subscriber is not None:
                subscriber.process(create_user_from_orm(user))
        elif request.request_type == RequestType.READ:
            try:
                if request.id is not None:
                    user = User.get(User.id == request.id)
                    subscriber.process(create_user_from_orm(user))
                elif request.name is not None:
                    user = User.get(User.username == request.name)
                    subscriber.process(create_user_from_orm(user))
                else:
                    subscriber.process(None)
            except DoesNotExist:
                subscriber.process(None)
        elif request.request_type == RequestType.DELETE:
            User.delete().where(User.id == request.id).execute()
