from typing import Optional

from peewee import ModelSelect, DoesNotExist

from beb_lib import (AccessType,
                     Board,
                     CardsList,
                     Card)

from .storage_models import (BaseModel,
                             BoardModel,
                             CardListModel,
                             BoardUserAccess,
                             CardListUserAccess,
                             CardModel,
                             CardUserAccess)


def _create_access_type(query: ModelSelect):
    if query.count == 0:
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

    return _create_access_type(query)


def check_access_to_task(card: CardModel, user_id: int) -> AccessType:
    query = (CardUserAccess
             .select()
             .join(BoardModel)
             .where((CardUserAccess.user_id == user_id) & (CardUserAccess.card == card)))

    return _create_access_type(query)


def _get_orm_model(object_type: object, object_id: int, user_id: int) -> Optional[BaseModel]:
    class_name = object_type.__name__

    try:
        orm_model = None
        if class_name == Board.__name__:
            orm_model = BoardUserAccess.get(
                (BoardUserAccess.board == object_id) & (BoardUserAccess.user_id == user_id))
        elif class_name == CardsList.__name__:
            orm_model = CardListUserAccess.get(
                (CardListUserAccess.card_list == object_id) & (CardListUserAccess.user_id == user_id))
        elif class_name == Card.__name__:
            orm_model = CardUserAccess.get(
                (CardUserAccess.card == object_id) & (CardUserAccess.user_id == user_id))
        return orm_model
    except DoesNotExist:
        return None


def add_right(object_type: object, object_id: int, user_id: int, access_type: AccessType) -> None:
    """

    :param object_type: Pass here ORM class from storage_models model
    :param object_id: The Id of the ORM object that access_type should be added
    :param user_id: The id of the user whose access level is needed to be configured
    :param access_type: Types from AccessType enum (eg. READ, WRITE, READ_WRITE) that would be added to access_type
    of the object for provided user
    """
    orm_model = _get_orm_model(object_type, object_id, user_id)

    if orm_model:
        orm_model.access_type |= access_type
        orm_model.save()


def remove_right(object_type: object, object_id: int, user_id: int, access_type: AccessType) -> None:
    """

        :param object_type: Pass here ORM class from storage_models model
        :param object_id: The id of the ORM object that access_type should be removed
        :param user_id: The id of the user whose access level is needed to be configured
        :param access_type: Types from AccessType enum (eg. READ, WRITE, READ_WRITE) that would be removed from
        access_typeof the object for provided user
        """
    orm_model = _get_orm_model(object_type, object_id, user_id)

    if orm_model:
        orm_model.access_type |= access_type
        orm_model.access_type ^= access_type
        orm_model.save()
