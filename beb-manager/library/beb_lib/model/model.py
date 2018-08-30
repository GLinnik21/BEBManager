import random
from typing import List

from beb_lib import Board, RequestType, AccessType, CardsList
from beb_lib.model.exceptions import BoardDoesNotExistError, AccessDeniedError, Error
from beb_lib.storage import (StorageProvider,
                             BoardDataRequest,
                             CardDataRequest,
                             ListDataRequest,
                             AddAccessRightRequest,
                             RemoveAccessRightRequest,
                             IStorageProviderProtocol,
                             StorageProviderErrors)


class Model:
    """
    Base mediator and wrapper above all requests.
    """

    def __init__(self, path_to_db: str, custom_storage_provider: IStorageProviderProtocol = None):
        if custom_storage_provider is not None:
            self.storage_provider = custom_storage_provider
        else:
            self.storage_provider = StorageProvider(path_to_db)
        self.storage_provider.open()

    def add_right(self, object_id: int, object_type: type, user_id: int, access_type: AccessType):
        request = AddAccessRightRequest(request_id=random.randrange(1000000),
                                        request_type=None,
                                        object_id=object_id,
                                        object_type=object_type,
                                        user_id=user_id,
                                        access_type=access_type)

        self.storage_provider.execute(request)

    def remove_right(self, object_id: int, object_type: type, user_id: int, access_type: AccessType):
        request = RemoveAccessRightRequest(request_id=random.randrange(1000000),
                                           request_type=None,
                                           object_id=object_id,
                                           object_type=object_type,
                                           user_id=user_id,
                                           access_type=access_type)

        self.storage_provider.execute(request)

    def board_read(self, board_id: int = None, board_name: str = None, request_user_id: int = None) -> List[Board]:
        request = BoardDataRequest(request_id=random.randrange(1000000),
                                   request_user_id=request_user_id,
                                   id=board_id,
                                   name=board_name,
                                   request_type=RequestType.READ)
        response, error = self.storage_provider.execute(request)

        if error is not None:
            if error.code == StorageProviderErrors.ACCESS_DENIED:
                raise AccessDeniedError(error.description)
            elif error.code == StorageProviderErrors.BOARD_DOES_NOT_EXIST:
                raise BoardDoesNotExistError(error.description)
            else:
                raise Error("""Undefined DB exception! 
                                Code: {} Description: {}""".format(error.error, error.description))

        return response.boards

    def board_write(self, board_id: int = None, board_name: str = None, request_user_id: int = None) -> Board:
        request = BoardDataRequest(request_id=random.randrange(1000000),
                                   request_user_id=request_user_id,
                                   id=board_id,
                                   name=board_name,
                                   request_type=RequestType.WRITE)
        response, error = self.storage_provider.execute(request)

        if error is not None:
            if error.code == StorageProviderErrors.ACCESS_DENIED:
                raise AccessDeniedError(error.description)
            else:
                raise Error("""Undefined DB exception! 
                Code: {} Description: {}""".format(error.error, error.description))

        return response.boards[0]

    def board_delete(self, board_id: int = None, board_name: str = None, request_user_id: int = None) -> None:
        request = BoardDataRequest(request_id=random.randrange(1000000),
                                   request_user_id=request_user_id,
                                   id=board_id,
                                   name=board_name,
                                   request_type=RequestType.DELETE)
        response, error = self.storage_provider.execute(request)

        if error is not None:
            if error.code == StorageProviderErrors.ACCESS_DENIED:
                raise AccessDeniedError(error.description)
            elif error.code == StorageProviderErrors.BOARD_DOES_NOT_EXIST:
                raise BoardDoesNotExistError(error.description)
            else:
                raise Error("""Undefined DB exception! 
                Code: {} Description: {}""".format(error.code, error.description))

    def list_read(self, list_id: int = None, board_id: int = None, list_name: str = None,
                  request_user_id: int = None) -> CardsList:
        request = ListDataRequest(request_id=random.randrange(1000000),
                                  request_user_id=request_user_id,
                                  id=list_id,
                                  board_id=board_id,
                                  name=list_name,
                                  request_type=RequestType.READ)

        response, error = self.storage_provider.execute(request)

        if error is not None:
            if error.code == StorageProviderErrors.ACCESS_DENIED:
                raise AccessDeniedError(error.description)
            elif error.code == StorageProviderErrors.LIST_DOES_NOT_EXIST:
                raise BoardDoesNotExistError(error.description)
            else:
                raise Error("""Undefined DB exception! 
                                Code: {} Description: {}""".format(error.error, error.description))

        return response.lists

    def list_write(self, list_id: int = None, board_id: int = None, list_name: str = None,
                   request_user_id: int = None) -> CardsList:
        request = ListDataRequest(request_id=random.randrange(1000000),
                                  request_user_id=request_user_id,
                                  id=list_id,
                                  board_id=board_id,
                                  name=list_name,
                                  request_type=RequestType.WRITE)

        response, error = self.storage_provider.execute(request)

        if error is not None:
            if error.code == StorageProviderErrors.ACCESS_DENIED:
                raise AccessDeniedError(error.description)
            else:
                raise Error("""Undefined DB exception! 
                Code: {} Description: {}""".format(error.error, error.description))

        return response.lists[0]

    def list_delete(self, list_id: int = None, board_id: int = None, list_name: str = None,
                    request_user_id: int = None) -> None:
        request = ListDataRequest(request_id=random.randrange(1000000),
                                  request_user_id=request_user_id,
                                  id=list_id,
                                  board_id=board_id,
                                  name=list_name,
                                  request_type=RequestType.DELETE)

        response, error = self.storage_provider.execute(request)

        if error is not None:
            if error.code == StorageProviderErrors.ACCESS_DENIED:
                raise AccessDeniedError(error.description)
            else:
                raise Error("""Undefined DB exception! 
                Code: {} Description: {}""".format(error.error, error.description))


