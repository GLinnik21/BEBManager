from typing import List

from peewee import (DoesNotExist)

import beb_lib.storage.provider as provider
from beb_lib.domain_entities.card_list import CardsList
from beb_lib.domain_entities.supporting import AccessType
from beb_lib.provider_interfaces import RequestType, BaseError
from beb_lib.storage.access_validator import (check_access_to_board,
                                              check_access_to_list
                                              )
from beb_lib.storage.models import (BoardModel,
                                    CardListModel,
                                    CardListUserAccess
                                    )
from beb_lib.storage.processors.card_processor import _delete_card
from beb_lib.storage.provider_requests import (BoardDataRequest)

METHOD_MAP = {
    RequestType.WRITE: lambda request, user_id, board_model: write_list(request, board_model, user_id),
    RequestType.READ: lambda request, user_id, board_model: read_list(request, board_model, user_id),
    RequestType.DELETE: lambda request, user_id, board_model: delete_list(request, user_id)
}


def _delete_list(card_list: CardListModel):
    CardListUserAccess.delete().where(CardListUserAccess.card_list == card_list)
    for card in card_list.cards:
        _delete_card(card)
    card_list.delete_instance()


def write_list(request: BoardDataRequest, board: BoardModel, user_id: int) -> (List[CardsList], BaseError):
    try:
        card_list = CardListModel.get(CardListModel.id == request.id)

        if bool(check_access_to_list(card_list, user_id) & AccessType.WRITE):
            card_list.name = request.name
            card_list.save()
            cards = [card_id for card_id in card_list.cards]
            if board is not None:
                card_list.board = board

            return [CardsList(card_list.name, card_list.id, cards)], None
        else:
            return None, BaseError(provider.StorageProviderErrors.ACCESS_DENIED, "This user can't write to this list")
    except DoesNotExist:
        if bool(check_access_to_board(board, user_id) & AccessType.WRITE):
            card_list = CardListModel.create(name=request.name, board=board)
            CardListUserAccess.create(user_id=user_id, card_list=card_list)
            return [CardsList(card_list.name, card_list.id)], None
        else:
            return None, BaseError(provider.StorageProviderErrors.ACCESS_DENIED, "This user has not enough rights for "
                                                                                 "this board")


def read_list(request: BoardDataRequest, board: BoardModel, user_id: int) -> (List[CardsList], BaseError):
    query = CardListModel.select()
    list_response = []

    if request.id is not None:
        query = query.where(CardListModel.id == request.id)
    if request.name is not None:
        query = query.where(CardListModel.name == request.name)
    if board is not None:
        query = query.where(CardListModel.board == board)

    if query.count() == 0:
        return None, BaseError(code=provider.StorageProviderErrors.LIST_DOES_NOT_EXIST,
                               description="List doesn't exist")

    for card_list in query:
        if bool(check_access_to_list(card_list, user_id) & AccessType.READ):
            cards = [card_id for card_id in card_list.cards]
            list_response += [CardsList(card_list.name, card_list.id, cards)]

    if not list_response:
        return None, BaseError(code=provider.StorageProviderErrors.ACCESS_DENIED,
                               description="This user can't read this list")
    else:
        return list_response, None


def delete_list(request: BoardDataRequest, user_id: int) -> (List[CardsList], BaseError):
    try:
        card_list = CardListModel.get(CardListModel.id == request.id)
        access = check_access_to_list(card_list, user_id)
        if bool(access & AccessType.WRITE):
            CardListUserAccess.delete().where(CardListUserAccess.card_list == card_list).execute()
            _delete_list(card_list)
        else:
            return None, BaseError(code=provider.StorageProviderErrors.ACCESS_DENIED,
                                   description="This user can't delete this list")
    except DoesNotExist:
        return None, BaseError(code=provider.StorageProviderErrors.LIST_DOES_NOT_EXIST,
                               description="List doesn't exist")
    return None, None


def process_list_call(request: BoardDataRequest) -> (provider.ListDataResponse, BaseError):
    try:
        board = BoardModel.get(BoardModel.id == request.board_id) if request.board_id is not None else None
        user_id = request.request_user_id
        list_response, error = METHOD_MAP[request.request_type](request, user_id, board)

        return provider.ListDataResponse(lists=list_response, request_id=request.request_id), error
    except DoesNotExist:
        return None, BaseError(code=provider.StorageProviderErrors.BOARD_DOES_NOT_EXIST,
                               description="Board doesn't exist")
