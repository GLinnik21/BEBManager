from collections import namedtuple
import enum
from typing import List

from peewee import (SqliteDatabase,
                    DoesNotExist)

from beb_lib import (IProvider,
                     BaseError,
                     RequestType,
                     AccessType,
                     Board,
                     CardsList,
                     RESPONSE_BASE_FIELDS,
                     CARD_LIST_DEFAULTS)

from .access_validator import (check_access_to_board,
                               check_access_to_list,
                               check_access_to_task,
                               add_right,
                               remove_right)

from .models import (BoardModel,
                     CardListModel,
                     TagModel,
                     CardModel,
                     TagCard,
                     CardUserAccess,
                     CardListUserAccess,
                     BoardUserAccess,
                     DATABASE_PROXY)

from .provider_requests import (BoardDataRequest,
                                ListDataRequest,
                                AddAccessRightRequest,
                                RemoveAccessRightRequest)

from .provider_protocol import IStorageProviderProtocol

BoardDataResponse = namedtuple('BoardDataResponse', RESPONSE_BASE_FIELDS + ['boards'])
ListDataResponse = namedtuple('ListDataResponse', RESPONSE_BASE_FIELDS + ['lists'])


@enum.unique
class StorageProviderErrors(enum.IntEnum):
    ACCESS_DENIED = enum.auto()
    BOARD_DOES_NOT_EXIST = enum.auto()
    LIST_DOES_NOT_EXIST = enum.auto()


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

    def execute(self, request: namedtuple) -> (namedtuple, BaseError):
        if type(request).__name__ == BoardDataRequest.__name__:
            return StorageProvider._process_board_call(request)
        elif type(request).__name__ == ListDataRequest.__name__:
            return StorageProvider._process_list_call(request)
        elif type(request).__name__ == AddAccessRightRequest.__name__:
            add_right(request.object_type, request.object_id, request.user_id, request.access_type)
            return None, None
        elif type(request).__name__ == RemoveAccessRightRequest.__name__:
            remove_right(request.object_type, request.object_id, request.user_id, request.access_type)
            return None, None

    @staticmethod
    def _create_board_with_defaults(board_name: str, user_id: int) -> List[Board]:
        board = BoardModel.create(name=board_name)
        BoardUserAccess.create(user_id=user_id, board=board)
        board_response = [Board(board.name, board.id)]

        for name in CARD_LIST_DEFAULTS:
            CardListModel.create(name=name, board=board)

        return board_response

    @staticmethod
    def _delete_card(card: CardModel):
        CardUserAccess.delete().where(CardUserAccess.card == card).execute()
        TagCard.delete().where(TagCard.card == card).execute()
        card.delete_instance()

    @staticmethod
    def _delete_list(card_list: CardListModel):
        CardListUserAccess.delete().where(CardListUserAccess.card_list == card_list)
        for card in card_list.cards:
            StorageProvider._delete_card(card)
        card_list.delete_instance()

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
                board_response = StorageProvider._create_board_with_defaults(request.name, user_id)
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
                    BoardUserAccess.delete().where(BoardUserAccess.board == board).execute()
                    for card_list in board.card_lists:
                        StorageProvider._delete_list(card_list)
                    board.delete_instance()
                else:
                    return None, BaseError(code=StorageProviderErrors.ACCESS_DENIED,
                                           description="This user can't delete this board")
            except DoesNotExist:
                return None, BaseError(code=StorageProviderErrors.BOARD_DOES_NOT_EXIST,
                                       description="Board doesn't exist")

        return BoardDataResponse(boards=board_response, request_id=request.request_id), None

    @staticmethod
    def _process_list_call(request: BoardDataRequest) -> (namedtuple, BaseError):
        user_id = request.request_user_id
        list_response = None
        board = None

        try:
            board = BoardModel.get(BoardModel.id == request.board_id)
            access_to_board = check_access_to_board(board, request.request_user_id)

            required_access = None
            if request.request_type == RequestType.WRITE or request.request_type == RequestType.DELETE:
                required_access = AccessType.WRITE
            else:
                required_access = AccessType.READ

            if not bool(access_to_board & required_access):
                return None, BaseError(StorageProviderErrors.ACCESS_DENIED, "This user has not enough rights for this "
                                                                            "board")
        except DoesNotExist:
            return None, BaseError(code=StorageProviderErrors.BOARD_DOES_NOT_EXIST,
                                   description="Board doesn't exist")

        if request.request_type == RequestType.WRITE:
            try:
                card_list = None
                if request.id is not None:
                    card_list = CardListModel.get(CardListModel.id == request.id)
                elif request.name is not None:
                    card_list = CardListModel.get(CardListModel.name == request.name)

                if bool(check_access_to_list(card_list, user_id) & AccessType.WRITE):
                    card_list.name = request.name
                    card_list.board = board
                    card_list.save()
                    cards = [card_id for card_id in card_list.cards]
                    list_response = [CardsList(card_list.name, card_list.id, cards)]
                else:
                    return None, BaseError(StorageProviderErrors.ACCESS_DENIED, "This user can't write to this list")
            except DoesNotExist:
                card_list = CardListModel.create(name=request.name, board=board)
                CardListUserAccess.create(user_id=user_id, card_list=card_list)
                list_response = [CardsList(card_list.name, card_list.id)]
        elif request.request_type == RequestType.READ:
            if request.id is None and request.name is None:
                list_response = []
                query = CardListModel.select()
                for card_list in query:
                    if bool(check_access_to_list(card_list, user_id) & AccessType.READ):
                        cards = [card_id for card_id in card_list.cards]
                        list_response += [CardsList(card_list.name, card_list.id, cards)]
            else:
                try:
                    card_list = CardListModel.get((CardListModel.id == request.id) |
                                                  (CardListModel.name == request.name))
                    if bool(check_access_to_list(card_list, user_id) & AccessType.READ):
                        cards = [card_id for card_id in card_list.cards]
                        list_response = [CardsList(card_list.name, card_list.id, cards)]
                    else:
                        return None, BaseError(code=StorageProviderErrors.ACCESS_DENIED,
                                               description="This user can't read this list")
                except DoesNotExist:
                    return None, BaseError(code=StorageProviderErrors.LIST_DOES_NOT_EXIST,
                                           description="List doesn't exist")
        elif request.request_type == RequestType.DELETE:
            try:
                card_list = CardListModel.get((CardListModel.id == request.id) |
                                              (CardListModel.name == request.name))
                access = check_access_to_list(card_list, user_id)
                if bool(access & AccessType.WRITE):
                    CardListUserAccess.delete().where(CardListUserAccess.card_list == card_list).execute()
                    StorageProvider._delete_list(card_list)
                else:
                    return None, BaseError(code=StorageProviderErrors.ACCESS_DENIED,
                                           description="This user can't delete this list")
            except DoesNotExist:
                return None, BaseError(code=StorageProviderErrors.LIST_DOES_NOT_EXIST,
                                       description="List doesn't exist")

        return ListDataResponse(lists=list_response, request_id=request.request_id), None
