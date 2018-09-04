from typing import List

from peewee import DoesNotExist

import beb_lib.storage.processors.list_processor as list_processor
from beb_lib.domain_entities.board import Board
from beb_lib.domain_entities.card import CARD_LIST_DEFAULTS
from beb_lib.domain_entities.supporting import AccessType
from beb_lib.provider_interfaces import RequestType, BaseError
from beb_lib.storage.access_validator import check_access_to_board
from beb_lib.storage.models import (CardListModel,
                                    BoardModel,
                                    BoardUserAccess
                                    )
from beb_lib.storage.provider import BoardDataResponse, StorageProviderErrors
from beb_lib.storage.provider_requests import BoardDataRequest

METHOD_MAP = {
    RequestType.WRITE: lambda request, user_id: write_board(request, user_id),
    RequestType.READ: lambda request, user_id: read_board(request, user_id),
    RequestType.DELETE: lambda request, user_id: delete_board(request, user_id)
}


def _create_board_with_defaults(board_name: str, user_id: int) -> List[Board]:
    board = BoardModel.create(name=board_name)
    BoardUserAccess.create(user_id=user_id, board=board)
    board_response = [Board(board.name, board.id)]

    for name in CARD_LIST_DEFAULTS:
        CardListModel.create(name=name, board=board)

    return board_response


def write_board(request: BoardDataRequest, user_id: int) -> (List[Board], BaseError):
    try:
        board = None
        if request.id is not None:
            board = BoardModel.get(BoardModel.id == request.id)
        elif request.name is not None:
            board = BoardModel.get(BoardModel.name == request.name)

        if bool(check_access_to_board(board, user_id) & AccessType.WRITE):
            board.name = request.name
            board.save()
            lists = [list_id for list_id in board.card_lists]
            return [Board(board.name, board.id, lists)], None
        else:
            return None, BaseError(StorageProviderErrors.ACCESS_DENIED, "This user can't write to this board")
    except DoesNotExist:
        return [_create_board_with_defaults(request.name, user_id)], None


def read_board(request: BoardDataRequest, user_id: int) -> (List[Board], BaseError):
    if request.id is None and request.name is None:
        board_response = []
        query = BoardModel.select()
        for board in query:
            if bool(check_access_to_board(board, user_id) & AccessType.READ):
                lists = [list_id for list_id in board.card_lists]
                board_response += [Board(board.name, board.id, lists)]
        return board_response, None
    else:
        try:
            board = BoardModel.get((BoardModel.id == request.id) | (BoardModel.name == request.name))
            if bool(check_access_to_board(board, user_id) & AccessType.READ):
                lists = [list_id for list_id in board.card_lists]
                return [Board(board.name, board.id, lists)], None
            else:
                return None, BaseError(code=StorageProviderErrors.ACCESS_DENIED,
                                       description="This user can't read this board")
        except DoesNotExist:
            return None, BaseError(code=StorageProviderErrors.BOARD_DOES_NOT_EXIST,
                                   description="Board doesn't exist")


def delete_board(request: BoardDataRequest, user_id: int) -> (List[Board], BaseError):
    try:
        board = BoardModel.get((BoardModel.id == request.id) | (BoardModel.name == request.name))
        access = check_access_to_board(board, user_id)
        if bool(access & AccessType.WRITE):
            BoardUserAccess.delete().where(BoardUserAccess.board == board).execute()
            for card_list in board.card_lists:
                list_processor._delete_list(card_list)
            board.delete_instance()
        else:
            return None, BaseError(code=StorageProviderErrors.ACCESS_DENIED,
                                   description="This user can't delete this board")
    except DoesNotExist:
        return None, BaseError(code=StorageProviderErrors.BOARD_DOES_NOT_EXIST,
                               description="Board doesn't exist")


def process_board_call(request: BoardDataRequest) -> (BoardDataResponse, BaseError):
    user_id = request.request_user_id

    board_response, error = METHOD_MAP[request.request_type](request, user_id)
    return BoardDataResponse(boards=board_response, request_id=request.request_id), error
