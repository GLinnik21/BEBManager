from collections import namedtuple
from typing import List

from peewee import SqliteDatabase
from enum import IntEnum, unique, auto

from beb_lib.storage.provider_protocol import IStorageProviderProtocol
from beb_lib.provider_interfaces import (REQUEST_BASE_FIELDS,
                                         RESPONSE_BASE_FIELDS,
                                         IProvider,
                                         BaseError,
                                         RequestType
                                         )

from beb_manager_cli.storage.user import DATABASE_PROXY, User, create_user_from_orm

UserDataRequest = namedtuple('UserDataRequest', REQUEST_BASE_FIELDS + ['id', 'name'])
UserDataResponse = namedtuple('UserDataResponse', RESPONSE_BASE_FIELDS + ['users'])


@unique
class UserProviderErrorCodes(IntEnum):
    USER_DOES_NOT_EXIST = auto()


class UserProvider(IProvider, IStorageProviderProtocol):
    """
    Instance to interact with user data base that relates to beb_manager_cli layer
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
        user_response, error = self._database_call(request)
        return UserDataResponse(users=user_response, request_id=request.request_id), error

    @staticmethod
    def _database_call(request: namedtuple) -> (List[User], BaseError):
        if request.request_type == RequestType.WRITE:
            user = User.create(id=request.id, username=request.name)
            return [create_user_from_orm(user)], None
        elif request.request_type == RequestType.READ:
            query = User.select()

            if request.id is not None or request.name is not None:
                query = query.where((User.id == request.id) | (User.username == request.name))

            if query.count() == 0:
                return None, BaseError(code=UserProviderErrorCodes.USER_DOES_NOT_EXIST, description="User doesn't "
                                                                                                    "exist")
            return [create_user_from_orm(orm_user) for orm_user in query], None
        elif request.request_type == RequestType.DELETE:
            User.delete().where(User.id == request.id).execute()
