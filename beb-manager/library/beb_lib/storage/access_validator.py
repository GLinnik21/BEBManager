from typing import Optional
import peewee
from peewee import DoesNotExist

from beb_lib.domain_entities.board import Board
from beb_lib.domain_entities.card import Card
from beb_lib.domain_entities.card_list import CardsList
from beb_lib.domain_entities.supporting import AccessType
from beb_lib.provider_interfaces import RequestType
from beb_lib.storage.models import (BaseModel,
                                    BoardModel,
                                    CardListModel,
                                    BoardUserAccess,
                                    CardListUserAccess,
                                    CardModel,
                                    CardUserAccess
                                    )


def _create_access_type(query: peewee.ModelSelect):
    if query.count() == 0:
        return AccessType.READ_WRITE
    else:
        return AccessType(query[0].access_type)


def check_access_to_board(board: BoardModel, user_id: int) -> AccessType:
    query = (BoardUserAccess
             .select()
             .join(BoardModel)
             .where((BoardUserAccess.user_id == user_id) & (BoardUserAccess.board == board)))

    return _create_access_type(query)


def check_access_to_list(card_list: CardListModel, user_id: int) -> AccessType:
    query = (CardListUserAccess
             .select()
             .join(CardListModel)
             .where((CardListUserAccess.user_id == user_id) & (CardListUserAccess.card_list == card_list)))

    return _create_access_type(query) & check_access_to_board(card_list.board, user_id)


def check_access_to_card(card: CardModel, user_id: int) -> AccessType:
    query = (CardUserAccess
             .select()
             .join(CardModel)
             .where((CardUserAccess.user_id == user_id) & (CardUserAccess.card == card)))

    return _create_access_type(query) & check_access_to_list(card.list, user_id)


def map_request_to_access_types(request_type: RequestType) -> AccessType:
    if request_type == RequestType.WRITE or request_type == RequestType.DELETE:
        return AccessType.WRITE
    else:
        return AccessType.READ


def _get_orm_model(object_type: object, object_id: int, user_id: int) -> Optional[BaseModel]:
    class_name = object_type.__name__

    try:
        if class_name == Board.__name__:
            return BoardUserAccess.get(
                (BoardUserAccess.board == object_id) & (BoardUserAccess.user_id == user_id))
        elif class_name == CardsList.__name__:
            return CardListUserAccess.get(
                (CardListUserAccess.card_list == object_id) & (CardListUserAccess.user_id == user_id))
        elif class_name == Card.__name__:
            return CardUserAccess.get(
                (CardUserAccess.card == object_id) & (CardUserAccess.user_id == user_id))
    except DoesNotExist:
        if class_name == Board.__name__:
            return BoardUserAccess.create(board=object_id, user_id=user_id, access_type=0)
        elif class_name == CardsList.__name__:
            return CardListUserAccess.create(card_list=object_id, user_id=user_id, access_type=0)
        elif class_name == Card.__name__:
            return CardUserAccess.create(card=object_id, user_id=user_id, access_type=0)


def add_right(object_type: object, object_id: int, user_id: int, access_type: AccessType) -> None:
    """

    :param object_type: Pass here class from domain_entities
    :param object_id: The Id of the ORM object that access_type should be added
    :param user_id: The id of the user whose access level is needed to be configured
    :param access_type: Types from AccessType enum (eg. READ, WRITE, READ_WRITE) that would be added to access_type
    of the object for provided user
    """
    orm_model = _get_orm_model(object_type, object_id, user_id)

    if orm_model:
        a_type = AccessType(orm_model.access_type)
        orm_model.access_type = (a_type | access_type).value
        orm_model.save()


def remove_right(object_type: object, object_id: int, user_id: int, access_type: AccessType) -> None:
    """

        :param object_type: Pass here class from domain_entities
        :param object_id: The id of the ORM object that access_type should be removed
        :param user_id: The id of the user whose access level is needed to be configured
        :param access_type: Types from AccessType enum (eg. READ, WRITE, READ_WRITE) that would be removed from
        access_typeof the object for provided user
        """
    orm_model = _get_orm_model(object_type, object_id, user_id)

    if orm_model:
        a_type = AccessType(orm_model.access_type)
        a_type |= access_type
        orm_model.access_type = (a_type ^ access_type).value
        orm_model.save()
