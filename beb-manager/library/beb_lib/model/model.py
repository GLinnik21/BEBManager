"""
This module provides all methods to work with library
"""
import datetime
import random
from typing import List, Optional

from beb_lib.logger import log_func, LIBRARY_LOGGER_NAME
from beb_lib.domain_entities.board import Board
from beb_lib.domain_entities.card import Card
from beb_lib.domain_entities.card_list import CardsList
from beb_lib.domain_entities.plan import Plan
from beb_lib.domain_entities.supporting import AccessType
from beb_lib.domain_entities.tag import Tag
from beb_lib.provider_interfaces import RequestType
from beb_lib.storage.provider import StorageProvider, StorageProviderErrors
from beb_lib.storage.provider_protocol import IStorageProviderProtocol
from beb_lib.storage.provider_requests import (BoardDataRequest,
                                               CardDataRequest,
                                               ListDataRequest,
                                               AddAccessRightRequest,
                                               RemoveAccessRightRequest,
                                               PlanDataRequest,
                                               TagDataRequest,
                                               GetAccessRightRequest,
                                               PlanTriggerRequest
                                               )
from beb_lib.model.exceptions import (BoardDoesNotExistError,
                                      ListDoesNotExistError,
                                      CardDoesNotExistError,
                                      AccessDeniedError,
                                      Error,
                                      TagDoesNotExistError,
                                      PlanDoesNotExistError,
                                      UniqueObjectDoesNotExistError
                                      )


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

    @log_func(LIBRARY_LOGGER_NAME)
    def get_right(self, object_id: int, object_type: type, user_id: int) -> AccessType:
        request = GetAccessRightRequest(request_id=random.randrange(1000000),
                                        request_type=RequestType.READ,
                                        object_id=object_id,
                                        object_type=object_type,
                                        user_id=user_id)
        access_type = self.storage_provider.execute(request)

        if access_type is None:
            raise UniqueObjectDoesNotExistError

        return access_type

    @log_func(LIBRARY_LOGGER_NAME)
    def add_right(self, object_id: int, object_type: type, user_id: int, access_type: AccessType) -> None:
        request = AddAccessRightRequest(request_id=random.randrange(1000000),
                                        request_type=RequestType.WRITE,
                                        object_id=object_id,
                                        object_type=object_type,
                                        user_id=user_id,
                                        access_type=access_type)

        self.storage_provider.execute(request)

    @log_func(LIBRARY_LOGGER_NAME)
    def remove_right(self, object_id: int, object_type: type, user_id: int, access_type: AccessType) -> None:
        request = RemoveAccessRightRequest(request_id=random.randrange(1000000),
                                           request_type=RequestType.WRITE,
                                           object_id=object_id,
                                           object_type=object_type,
                                           user_id=user_id,
                                           access_type=access_type)

        self.storage_provider.execute(request)

    @log_func(LIBRARY_LOGGER_NAME)
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
                                Code: {} Description: {}""".format(error.code, error.description))

        return response.boards

    @log_func(LIBRARY_LOGGER_NAME)
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
                Code: {} Description: {}""".format(error.code, error.description))

        return response.boards[0]

    @log_func(LIBRARY_LOGGER_NAME)
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

    @log_func(LIBRARY_LOGGER_NAME)
    def list_read(self, board_id: Optional[int], list_id: int = None, list_name: str = None,
                  request_user_id: int = None) -> List[CardsList]:
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
                raise ListDoesNotExistError(error.description)
            else:
                raise Error("""Undefined DB exception! 
                                Code: {} Description: {}""".format(error.code, error.description))

        return response.lists

    @log_func(LIBRARY_LOGGER_NAME)
    def list_write(self, board_id: int, list_id: int = None, list_name: str = None,
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
                Code: {} Description: {}""".format(error.code, error.description))

        return response.lists[0]

    @log_func(LIBRARY_LOGGER_NAME)
    def list_delete(self, list_id: int = None, list_name: str = None,
                    request_user_id: int = None) -> None:

        if self.storage_provider.archived_list_id == list_id:
            raise AccessDeniedError("You can't delete this list")

        request = ListDataRequest(request_id=random.randrange(1000000),
                                  request_user_id=request_user_id,
                                  id=list_id,
                                  board_id=None,
                                  name=list_name,
                                  request_type=RequestType.DELETE)

        response, error = self.storage_provider.execute(request)

        if error is not None:
            if error.code == StorageProviderErrors.ACCESS_DENIED:
                raise AccessDeniedError(error.description)
            elif error.code == StorageProviderErrors.LIST_DOES_NOT_EXIST:
                raise ListDoesNotExistError(error.description)
            else:
                raise Error("""Undefined DB exception! 
                Code: {} Description: {}""".format(error.code, error.description))

    @log_func(LIBRARY_LOGGER_NAME)
    def card_read(self, list_id: Optional[int], card_id: int = None, card_name: str = None, tag_id: int = None,
                  board_id: int = None, request_user_id: int = None) -> List[Card]:
        request = CardDataRequest(request_id=random.randrange(1000000),
                                  id=card_id,
                                  request_user_id=request_user_id,
                                  name=card_name,
                                  description=None,
                                  expiration_date=None,
                                  priority=None,
                                  assignee=None,
                                  children=None,
                                  tags=[tag_id] if tag_id is not None else [],
                                  list_id=list_id,
                                  board_id=board_id,
                                  request_type=RequestType.READ)

        response, error = self.storage_provider.execute(request)

        if error is not None:
            if error.code == StorageProviderErrors.ACCESS_DENIED:
                raise AccessDeniedError(error.description)
            elif error.code == StorageProviderErrors.CARD_DOES_NOT_EXIST:
                raise CardDoesNotExistError(error.description)
            else:
                raise Error("""Undefined DB exception! 
                                Code: {} Description: {}""".format(error.code, error.description))

        for card in response.cards:
            try:
                card.plan = self.plan_read(card.user_id, request_user_id)
            except Error:
                pass

        return response.cards

    @log_func(LIBRARY_LOGGER_NAME)
    def card_write(self, list_id: Optional[int], card_instance: Card, request_user_id: int = None) -> Card:
        request = CardDataRequest(request_id=random.randrange(1000000),
                                  id=card_instance.unique_id,
                                  request_user_id=request_user_id,
                                  name=card_instance.name,
                                  description=card_instance.description,
                                  expiration_date=card_instance.expiration_date,
                                  priority=card_instance.priority,
                                  assignee=card_instance.assignee_id,
                                  children=card_instance.children,
                                  tags=card_instance.tags,
                                  list_id=list_id,
                                  board_id=None,
                                  request_type=RequestType.WRITE)

        response, error = self.storage_provider.execute(request)

        if error is not None:
            if error.code == StorageProviderErrors.ACCESS_DENIED:
                raise AccessDeniedError(error.description)
            else:
                raise Error("""Undefined DB exception! 
                Code: {} Description: {}""".format(error.code, error.description))

        return response.cards[0]

    @log_func(LIBRARY_LOGGER_NAME)
    def card_delete(self, card_id: int = None, card_name: str = None,
                    request_user_id: int = None) -> None:
        request = CardDataRequest(request_id=random.randrange(1000000),
                                  id=card_id,
                                  request_user_id=request_user_id,
                                  name=card_name,
                                  description=None,
                                  expiration_date=None,
                                  priority=None,
                                  assignee=None,
                                  children=None,
                                  tags=None,
                                  list_id=None,
                                  board_id=None,
                                  request_type=RequestType.DELETE)

        response, error = self.storage_provider.execute(request)

        if error is not None:
            if error.code == StorageProviderErrors.ACCESS_DENIED:
                raise AccessDeniedError(error.description)
            elif error.code == StorageProviderErrors.CARD_DOES_NOT_EXIST:
                raise CardDoesNotExistError(error.description)
            else:
                raise Error("""Undefined DB exception! 
                Code: {} Description: {}""".format(error.code, error.description))

    @log_func(LIBRARY_LOGGER_NAME)
    def tag_read(self, tag_id: int = None, tag_name: str = None) -> List[Tag]:
        request = TagDataRequest(request_id=random.randrange(1000000),
                                 id=tag_id,
                                 name=tag_name,
                                 color=None,
                                 request_type=RequestType.READ)

        response, error = self.storage_provider.execute(request)

        if error is not None:
            if error.code == StorageProviderErrors.TAG_DOES_NOT_EXIST:
                raise TagDoesNotExistError(error.description)
            else:
                raise Error("""Undefined DB exception! 
                Code: {} Description: {}""".format(error.code, error.description))

        return response.tags

    @log_func(LIBRARY_LOGGER_NAME)
    def tag_write(self, tag_id: int = None, tag_name: str = None, color: int = None) -> Tag:
        request = TagDataRequest(request_id=random.randrange(1000000),
                                 id=tag_id,
                                 name=tag_name,
                                 color=color,
                                 request_type=RequestType.WRITE)

        response, error = self.storage_provider.execute(request)

        if error is not None:
            raise Error("""Undefined DB exception! 
            Code: {} Description: {}""".format(error.code, error.description))

        return response.tags[0]

    @log_func(LIBRARY_LOGGER_NAME)
    def tag_delete(self, tag_id: int = None, tag_name: str = None) -> None:
        request = TagDataRequest(request_id=random.randrange(1000000),
                                 id=tag_id,
                                 name=tag_name,
                                 color=None,
                                 request_type=RequestType.DELETE)

        response, error = self.storage_provider.execute(request)

        if error is not None:
            if error.code == StorageProviderErrors.TAG_DOES_NOT_EXIST:
                raise TagDoesNotExistError(error.description)
            else:
                raise Error("""Undefined DB exception! 
                Code: {} Description: {}""".format(error.code, error.description))

    @log_func(LIBRARY_LOGGER_NAME)
    def plan_read(self, card_id: int, request_user_id: int) -> Plan:
        request = PlanDataRequest(request_id=random.randrange(1000000),
                                  request_user_id=request_user_id,
                                  interval=None,
                                  last_created=None,
                                  card_id=card_id,
                                  request_type=RequestType.READ)

        response, error = self.storage_provider.execute(request)

        if error is not None:
            if error.code == StorageProviderErrors.ACCESS_DENIED:
                raise AccessDeniedError(error.description)
            elif error.code == StorageProviderErrors.CARD_DOES_NOT_EXIST:
                raise CardDoesNotExistError(error.description)
            elif error.code == StorageProviderErrors.PLAN_DOES_NOT_EXIST:
                raise PlanDoesNotExistError(error.description)
            else:
                raise Error("""Undefined DB exception! 
                            Code: {} Description: {}""".format(error.code, error.description))

        return response.plan

    @log_func(LIBRARY_LOGGER_NAME)
    def plan_write(self, card_id: int, request_user_id: int, interval: datetime.timedelta,
                   last_created: datetime.datetime) -> Plan:
        request = PlanDataRequest(request_id=random.randrange(1000000),
                                  request_user_id=request_user_id,
                                  interval=interval,
                                  last_created=last_created,
                                  card_id=card_id,
                                  request_type=RequestType.WRITE)

        response, error = self.storage_provider.execute(request)

        if error is not None:
            if error.code == StorageProviderErrors.ACCESS_DENIED:
                raise AccessDeniedError(error.description)
            elif error.code == StorageProviderErrors.CARD_DOES_NOT_EXIST:
                raise CardDoesNotExistError(error.description)
            else:
                raise Error("""Undefined DB exception! 
                                    Code: {} Description: {}""".format(error.code, error.description))

        return response.plan

    @log_func(LIBRARY_LOGGER_NAME)
    def plan_delete(self, card_id: int, request_user_id: int) -> None:
        request = PlanDataRequest(request_id=random.randrange(1000000),
                                  request_user_id=request_user_id,
                                  interval=None,
                                  last_created=None,
                                  card_id=card_id,
                                  request_type=RequestType.DELETE)

        response, error = self.storage_provider.execute(request)

        if error is not None:
            if error.code == StorageProviderErrors.ACCESS_DENIED:
                raise AccessDeniedError(error.description)
            elif error.code == StorageProviderErrors.CARD_DOES_NOT_EXIST:
                raise CardDoesNotExistError(error.description)
            elif error.code == StorageProviderErrors.PLAN_DOES_NOT_EXIST:
                raise PlanDoesNotExistError(error.description)
            else:
                raise Error("""Undefined DB exception! 
                                    Code: {} Description: {}""".format(error.code, error.description))

    @log_func(LIBRARY_LOGGER_NAME)
    def trigger_card_plan_creation(self):
        request = PlanTriggerRequest(request_id=random.randrange(1000000), request_type=RequestType.WRITE)
        self.storage_provider.execute(request)

    # region convenience methods
    @log_func(LIBRARY_LOGGER_NAME)
    def archive_card(self, card_id: int = None, card_name: str = None,
                     request_user_id: int = None) -> None:
        cards = self.card_read(card_id, card_name, request_user_id)
        self.card_write(self.storage_provider.archived_list_id, cards[0], request_user_id)

    @log_func(LIBRARY_LOGGER_NAME)
    def get_cards_in_board(self, board_id: int, user_id: int) -> List[Card]:
        cards = self.card_read(None, board_id=board_id, request_user_id=user_id)

        return cards

    @log_func(LIBRARY_LOGGER_NAME)
    def get_cards_owned_by_user(self, user_id: int) -> List[Card]:
        cards = self.card_read(None, request_user_id=user_id)
        return list(filter(lambda card: card.user_id == user_id, cards))

    @log_func(LIBRARY_LOGGER_NAME)
    def get_cards_assigned_user(self, user_id: int) -> List[Card]:
        cards = self.card_read(None, request_user_id=user_id)
        return list(filter(lambda card: card.assignee_id == user_id, cards))

    @log_func(LIBRARY_LOGGER_NAME)
    def get_archived_cards(self, user_id: int) -> List[Card]:
        return self.card_read(self.storage_provider.archived_list_id, request_user_id=user_id)

    @log_func(LIBRARY_LOGGER_NAME)
    def get_readable_cards(self, user_id: int) -> List[Card]:
        cards = self.card_read(None, request_user_id=user_id)
        return list(filter(lambda card: bool(self.get_right(card.unique_id, Card, user_id) & AccessType.READ), cards))

    @log_func(LIBRARY_LOGGER_NAME)
    def get_writable_cards(self, user_id: int) -> List[Card]:
        cards = self.card_read(None, request_user_id=user_id)
        return list(filter(lambda card: bool(self.get_right(card.unique_id, Card, user_id) & AccessType.WRITE), cards))
    # end region
