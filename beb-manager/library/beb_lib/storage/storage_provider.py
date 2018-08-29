from collections import namedtuple
from enum import IntEnum, auto, unique
from threading import Thread

from peewee import (SqliteDatabase,
                    DoesNotExist)

from beb_lib import (IProviderSubscriber,
                     IProvider,
                     BaseError,
                     RequestType,
                     AccessType,
                     Board,
                     RESPONSE_BASE_FIELDS)

from .access_validator import (check_access_to_board,
                               check_access_to_list,
                               check_access_to_task,
                               add_right,
                               remove_right)

from .storage_models import (BoardModel,
                             CardListModel,
                             TagModel,
                             CardModel,
                             TagCard,
                             CardUserAccess,
                             CardListUserAccess,
                             BoardUserAccess,
                             DATABASE_PROXY)

from .storage_provider_requests import (BoardDataRequest,
                                        AddAccessRightRequest,
                                        RemoveAccessRightRequest)

from .storage_provider_protocol import IStorageProviderProtocol

BoardDataResponse = namedtuple('BoardDataResponse', RESPONSE_BASE_FIELDS + ['boards'])


@unique
class StorageProviderErrors(IntEnum):
    ACCESS_DENIED = auto()
    BOARD_DOES_NOT_EXIST = auto()


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
        self.database.create_tables([BoardModel,
                                     CardListModel,
                                     TagModel,
                                     CardModel,
                                     TagCard,
                                     CardUserAccess,
                                     CardListUserAccess,
                                     BoardUserAccess])

    def close(self) -> None:
        self.database.close()
        self.is_connected = False

    def execute(self, request: namedtuple, subscriber: IProviderSubscriber = None) -> None:
        t = Thread(target=self._async_execute, args=(request, subscriber,))
        t.start()

    def sync_execute(self, request: namedtuple) -> (namedtuple, BaseError):
        return self._database_call(request)

    @staticmethod
    def _async_execute(request: namedtuple, subscriber: IProviderSubscriber = None) -> None:
        result = StorageProvider._database_call(request)
        subscriber.process(result)

    @staticmethod
    def _process_board_call(request: BoardDataRequest) -> (namedtuple, BaseError):
        user_id = request.request_user_id
        board_response = None

        if request.request_type == RequestType.WRITE:
            board = None
            try:
                if request.id is not None:
                    board = BoardModel.get(BoardModel.id == request.id)
                elif request.name is not None:
                    board = BoardModel.get(BoardModel.name == request.name)
            except DoesNotExist:
                pass

            if board is None:
                board = BoardModel.create(name=request.name)
                BoardUserAccess.create(user_id=user_id, board=board)
                board_response = [Board(board.name, board.id)]
            elif bool(check_access_to_board(board, user_id) & AccessType.WRITE):
                board.name = request.name
                board.save()
                lists = [list_id for list_id in board.card_lists]
                board_response = [Board(board.name, board.id, lists)]
            else:
                return None, BaseError(StorageProviderErrors.ACCESS_DENIED, "This user can't write to this board")
        elif request.request_type == RequestType.READ:
            if request.id is None and request.name is None:
                board_response = []
                query = BoardModel.select()
                for board in query:
                    if bool(check_access_to_board(board, user_id) & AccessType.READ):
                        lists = [list_id for list_id in board.card_lists]
                        board_response += [Board(board.name, board.id, lists)]
            else:
                try:
                    board = BoardModel.get((BoardModel.id == request.id) | (BoardModel.name == request.name))
                    if bool(check_access_to_board(board, user_id) & AccessType.READ):
                        lists = [list_id for list_id in board.card_lists]
                        board_response = [Board(board.name, board.id, lists)]
                    else:
                        return None, BaseError(code=StorageProviderErrors.ACCESS_DENIED,
                                               description="This user can't read this board")
                except DoesNotExist:
                    return None, BaseError(code=StorageProviderErrors.BOARD_DOES_NOT_EXIST,
                                           description="Board doesn't exist")
        elif request.request_type == RequestType.DELETE:
            try:
                board = BoardModel.get((BoardModel.id == request.id) | (BoardModel.name == request.name))
                access = check_access_to_board(board, user_id)
                if bool(access & AccessType.WRITE):
                    BoardModel.delete().where(BoardModel.id == request.id).execute()
                    BoardUserAccess.delete().where(BoardUserAccess.board_id == request.id).execute()
                else:
                    return None, BaseError(code=StorageProviderErrors.ACCESS_DENIED,
                                           description="This user can't delete this board")
            except DoesNotExist:
                return None, BaseError(code=StorageProviderErrors.BOARD_DOES_NOT_EXIST,
                                       description="Board doesn't exist")

        return BoardDataResponse(boards=board_response, request_id=request.request_id), None

    @staticmethod
    def _database_call(request: namedtuple) -> (namedtuple, BaseError):
        if type(request).__name__ == BoardDataRequest.__name__:
            return StorageProvider._process_board_call(request)
        elif type(request).__name__ == AddAccessRightRequest.__name__:
            add_right(request.object_type, request.object_id, request.user_id, request.access_type)
            return None, None
        elif type(request).__name__ == RemoveAccessRightRequest.__name__:
            remove_right(request.object_type, request.object_id, request.user_id, request.access_type)
            return None, None
