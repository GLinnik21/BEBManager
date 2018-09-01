from collections import namedtuple
from typing import List

from peewee import DoesNotExist

import beb_lib.storage.provider as provider
from beb_lib.domain_entities import Card, Priority, AccessType
from beb_lib.provider_interfaces import RequestType, BaseError
from beb_lib.storage.access_validator import (check_access_to_board,
                                              check_access_to_list,
                                              check_access_to_card,
                                              map_request_to_access_types)
from beb_lib.storage.models import (CardListModel,
                                    TagModel,
                                    CardModel,
                                    TagCard,
                                    ParentChild,
                                    CardUserAccess)
from beb_lib.storage.provider_requests import (CardDataRequest)

METHOD_MAP = {
    RequestType.WRITE: lambda request, user_id, list_model: write_card(request, user_id, list_model),
    RequestType.READ: lambda request, user_id, list_model: read_card(request, user_id),
    RequestType.DELETE: lambda request, user_id, list_model: delete_card(request, user_id)
}


def _delete_card(card: CardModel):
    CardUserAccess.delete().where(CardUserAccess.card == card).execute()
    TagCard.delete().where(TagCard.card == card).execute()
    ParentChild.delete().where(ParentChild.parent == card).execute()
    card.delete_instance()


def _create_card_from_orm(card_model: CardModel) -> Card:
    children = []
    for parent_child in ParentChild.select().where(ParentChild.parent == card_model):
        children += [parent_child.child.id]

    tags = []
    for tag_card in TagCard.select().where(TagCard.card == card_model):
        tags += [tag_card.tag.id]

    return Card(card_model.name, card_model.id, card_model.user_id,
                card_model.assignee_id, card_model.description,
                card_model.expiration_date, card_model.priority,
                children, tags, card_model.created, card_model.last_modified)


def write_card(request: CardDataRequest, user_id: int, card_list: CardListModel) -> (List[Card], BaseError):
    try:
        card = None
        if request.id is not None:
            card = CardModel.get(CardModel.id == request.id)
        elif request.name is not None:
            card = CardModel.get(CardModel.name == request.name)

        if bool(check_access_to_card(card, user_id) & AccessType.WRITE):
            card.name = request.name
            card.description = request.description
            card.expiration_date = request.expiration_date
            card.priority = request.priority if request.priority is not None else Priority.MEDIUM
            card.assignee_id = request.assignee
            card.list = card_list

            actual_children_quarry = ParentChild.select().where(ParentChild.parent == card)
            for parent_child in actual_children_quarry:
                if bool(check_access_to_card(parent_child.child, user_id) & AccessType.READ) or \
                        parent_child.child.id not in request.children:
                    parent_child.delete_instance()

            if request.children is not None:
                potential_children_quarry = CardModel.select().where(CardModel.id.in_(request.children))
                for iter_card in potential_children_quarry:
                    if bool(check_access_to_card(iter_card, user_id) & AccessType.READ):
                        try:
                            ParentChild.get(ParentChild.parent == card, ParentChild.child == iter_card)
                        except DoesNotExist:
                            ParentChild.create(parent=card, child=iter_card)

            for tag_card in TagCard.select().where(TagCard.card == card):
                if tag_card.tag.id not in request.tags:
                    tag_card.delete_instance()

            if request.tags is not None:
                for tag in TagModel.select().where(TagModel.id.in_(request.tags)):
                    TagCard.create(tag=tag, card=card)

            card.save()
            return [_create_card_from_orm(card)], None
        else:
            return None, BaseError(provider.StorageProviderErrors.ACCESS_DENIED, "This user can't write to this card")
    except DoesNotExist:
        if bool(check_access_to_list(card_list, user_id) & AccessType.WRITE):
            card = CardModel.create(name=request.name,
                                    description=request.description,
                                    expiration_date=request.expiration_date,
                                    priority=Priority.MEDIUM if request.priority is None else request.priority,
                                    assignee_id=request.assignee,
                                    list=card_list,
                                    user_id=user_id)

            if request.tags is not None:
                for tag in TagModel.select().where(TagModel.id.in_(request.tags)):
                    TagCard.create(tag=tag, card=card)

            if request.children is not None:
                potential_children_quarry = CardModel.select().where(CardModel.id.in_(request.children))
                for iter_card in potential_children_quarry:
                    if bool(check_access_to_card(iter_card, user_id) & AccessType.READ):
                        ParentChild.create(parent=card, child=iter_card)

            return [_create_card_from_orm(card)], None
        else:
            return None, BaseError(provider.StorageProviderErrors.ACCESS_DENIED, "This user has not enough rights for "
                                                                                 "this list")


def read_card(request: CardDataRequest, user_id: int) -> (List[Card], BaseError):
    if request.id is None and request.name is None:
        card_response = []
        query = CardModel.select()
        for card in query:
            if bool(check_access_to_card(card, user_id) & AccessType.READ):
                card_response += [_create_card_from_orm(card)]
        return card_response, None
    else:
        try:
            card = CardModel.get((CardModel.id == request.id) | (CardModel.name == request.name))
            if bool(check_access_to_card(card, user_id) & AccessType.READ):
                return [_create_card_from_orm(card)], None
            else:
                return None, BaseError(code=provider.StorageProviderErrors.ACCESS_DENIED,
                                       description="This user can't read this card")
        except DoesNotExist:
            return None, BaseError(code=provider.StorageProviderErrors.LIST_DOES_NOT_EXIST,
                                   description="Card doesn't exist")


def delete_card(request: CardDataRequest, user_id: int) -> (List[Card], BaseError):
    try:
        card = CardModel.get((CardModel.id == request.id) | (CardModel.name == request.name))
        access = check_access_to_card(card, user_id)
        if bool(access & AccessType.WRITE):
            _delete_card(card)
        else:
            return None, BaseError(code=provider.StorageProviderErrors.ACCESS_DENIED,
                                   description="This user can't delete this card")
    except DoesNotExist:
        return None, BaseError(code=provider.StorageProviderErrors.LIST_DOES_NOT_EXIST,
                               description="Card doesn't exist")
    return None, None


def process_card_call(request: CardDataRequest) -> (namedtuple, BaseError):
    try:
        card_list = CardListModel.get(CardListModel.id == request.list_id) if request.list_id is not None else None
        user_id = request.request_user_id
        card_response, error = METHOD_MAP[request.request_type](request, user_id, card_list)

        return provider.CardDataResponse(cards=card_response, request_id=request.request_id), error
    except DoesNotExist:
        return None, BaseError(code=provider.StorageProviderErrors.LIST_DOES_NOT_EXIST,
                               description="List or board doesn't exist")
