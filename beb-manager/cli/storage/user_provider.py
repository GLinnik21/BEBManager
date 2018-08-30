from collections import namedtuple
from peewee import SqliteDatabase
from enum import IntEnum, unique, auto

from beb_lib import (IProvider,
                     IStorageProviderProtocol,
                     RequestType,
                     REQUEST_BASE_FIELDS,
                     RESPONSE_BASE_FIELDS,
                     BaseError)
from .user import (User,
                   create_user_from_orm,
                   DATABASE_PROXY)

UserDataRequest = namedtuple('UserDataRequest', REQUEST_BASE_FIELDS + ['id', 'name'])
UserDataResponse = namedtuple('UserDataResponse', RESPONSE_BASE_FIELDS + ['users'])


@unique
class UserProviderErrorCodes(IntEnum):
    USER_DOES_NOT_EXIST = auto()


class UserProvider(IProvider, IStorageProviderProtocol):
    """
    Instance to interact with user data base that relates to cli layer
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
        self.is_connected = False

    def execute(self, request: namedtuple) -> (namedtuple, BaseError):
        return self._database_call(request)

    @staticmethod
    def _database_call(request: namedtuple) -> (namedtuple, BaseError):
        user_response = None

        if request.request_type == RequestType.WRITE:
            user = User.create(id=request.id, username=request.name)
            user_response = [create_user_from_orm(user)]
        elif request.request_type == RequestType.READ:
            if request.id is None and request.name is None:
                query = User.select()
            else:
                query = User.select().where((User.id == request.id) | (User.username == request.name))
                if query.count() == 0:
                    return None, BaseError(code=UserProviderErrorCodes.USER_DOES_NOT_EXIST, description="User doesn't "
                                                                                                        "exist")
            user_response = [create_user_from_orm(orm_user) for orm_user in query]
        elif request.request_type == RequestType.DELETE:
            User.delete().where(User.id == request.id).execute()

        return UserDataResponse(users=user_response, request_id=request.request_id), None
