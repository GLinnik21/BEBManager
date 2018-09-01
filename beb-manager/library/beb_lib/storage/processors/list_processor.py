from typing import List
from peewee import (DoesNotExist)

import beb_lib.storage.provider as provider
from beb_lib.domain_entities import CardsList, AccessType
from beb_lib.provider_interfaces import RequestType, BaseError
from beb_lib.storage.processors.card_processor import _delete_card
from beb_lib.storage.provider_requests import (BoardDataRequest)
from beb_lib.storage.models import (BoardModel,
                                    CardListModel,
                                    CardListUserAccess)
from beb_lib.storage.access_validator import (check_access_to_board,
                                              check_access_to_list,
                                              map_request_to_access_types)

METHOD_MAP = {
    RequestType.WRITE: lambda request, user_id, board_model: write_list(request, board_model, user_id),
    RequestType.READ: lambda request, user_id: read_list(request, user_id),
    RequestType.DELETE: lambda request, user_id: delete_list(request, user_id)
}


def _delete_list(card_list: CardListModel):
    CardListUserAccess.delete().where(CardListUserAccess.card_list == card_list)
    for card in card_list.cards:
        _delete_card(card)
    card_list.delete_instance()


def write_list(request: BoardDataRequest, board: BoardModel, user_id: int) -> (List[CardsList], BaseError):
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
            return [CardsList(card_list.name, card_list.id, cards)], None
        else:
            return None, BaseError(provider.StorageProviderErrors.ACCESS_DENIED, "This user can't write to this list")
    except DoesNotExist:
        card_list = CardListModel.create(name=request.name, board=board)
        CardListUserAccess.create(user_id=user_id, card_list=card_list)
        return [CardsList(card_list.name, card_list.id)], None


def read_list(request: BoardDataRequest, user_id: int) -> (List[CardsList], BaseError):
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
                return [CardsList(card_list.name, card_list.id, cards)], None
            else:
                return None, BaseError(code=provider.StorageProviderErrors.ACCESS_DENIED,
                                       description="This user can't read this list")
        except DoesNotExist:
            return None, BaseError(code=provider.StorageProviderErrors.LIST_DOES_NOT_EXIST,
                                   description="List doesn't exist")


def delete_list(request: BoardDataRequest, user_id: int) -> (List[CardsList], BaseError):
    try:
        card_list = CardListModel.get((CardListModel.id == request.id) |
                                      (CardListModel.name == request.name))
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


def process_list_call(request: BoardDataRequest) -> (provider.ListDataResponse, BaseError):
    try:
        board = BoardModel.get(BoardModel.id == request.board_id)
        user_id = request.request_user_id
        access_to_board = check_access_to_board(board, request.request_user_id)
        required_access = map_request_to_access_types(request.request_type)

        if not bool(access_to_board & required_access):
            return None, BaseError(provider.StorageProviderErrors.ACCESS_DENIED, "This user has not enough rights for "
                                                                                 "this board")

        list_response, error = METHOD_MAP[request.request_type](request, user_id, board)

        return provider.ListDataResponse(lists=list_response, request_id=request.request_id), error
    except DoesNotExist:
        return None, BaseError(code=provider.StorageProviderErrors.BOARD_DOES_NOT_EXIST,
                               description="Board doesn't exist")
