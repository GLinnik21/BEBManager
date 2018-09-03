import datetime
import random
from typing import List

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
                                               TagDataRequest
                                               )
from beb_lib.model.exceptions import (BoardDoesNotExistError,
                                      ListDoesNotExistError,
                                      CardDoesNotExistError,
                                      AccessDeniedError,
                                      Error,
                                      TagDoesNotExistError,
                                      PlanDoesNotExistError
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
                                Code: {} Description: {}""".format(error.code, error.description))

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
                Code: {} Description: {}""".format(error.code, error.description))

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

    def list_read(self, list_id: int = None, list_name: str = None,
                  request_user_id: int = None) -> List[CardsList]:
        request = ListDataRequest(request_id=random.randrange(1000000),
                                  request_user_id=request_user_id,
                                  id=list_id,
                                  board_id=None,
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

    def list_delete(self, list_id: int = None, list_name: str = None,
                    request_user_id: int = None) -> None:
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

    def card_read(self, card_id: int = None, card_name: str = None,
                  request_user_id: int = None) -> List[Card]:
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

        return response.cards

    def card_write(self, list_id: int, card_instance: Card, request_user_id: int = None) -> Card:
        request = CardDataRequest(request_id=random.randrange(1000000),
                                  id=None,
                                  request_user_id=request_user_id,
                                  name=card_instance.name,
                                  description=card_instance.description,
                                  expiration_date=card_instance.expiration_date,
                                  priority=card_instance.priority,
                                  assignee=card_instance.assignee_id,
                                  children=card_instance.children,
                                  tags=card_instance.tags,
                                  list_id=list_id,
                                  request_type=RequestType.WRITE)

        response, error = self.storage_provider.execute(request)

        if error is not None:
            if error.code == StorageProviderErrors.ACCESS_DENIED:
                raise AccessDeniedError(error.description)
            else:
                raise Error("""Undefined DB exception! 
                Code: {} Description: {}""".format(error.code, error.description))

        return response.cards[0]

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

    def plan_read(self, card_id: int, user_id: int) -> Plan:
        request = PlanDataRequest(request_id=random.randrange(1000000),
                                  request_user_id=user_id,
                                  interval=None,
                                  last_created=None,
                                  card_id=card_id,
                                  request_type=RequestType.READ)

        plan, error = self.storage_provider.execute(request)

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

        return plan

    def plan_write(self, card_id: int, user_id: int, interval: datetime.timedelta,
                   last_created: datetime.datetime) -> Plan:
        request = PlanDataRequest(request_id=random.randrange(1000000),
                                  request_user_id=user_id,
                                  interval=interval,
                                  last_created=last_created,
                                  card_id=card_id,
                                  request_type=RequestType.WRITE)

        plan, error = self.storage_provider.execute(request)

        if error is not None:
            if error.code == StorageProviderErrors.ACCESS_DENIED:
                raise AccessDeniedError(error.description)
            elif error.code == StorageProviderErrors.CARD_DOES_NOT_EXIST:
                raise CardDoesNotExistError(error.description)
            else:
                raise Error("""Undefined DB exception! 
                                    Code: {} Description: {}""".format(error.code, error.description))

        return plan

    def plan_delete(self, card_id: int, user_id: int) -> None:
        request = PlanDataRequest(request_id=random.randrange(1000000),
                                  request_user_id=user_id,
                                  interval=None,
                                  last_created=None,
                                  card_id=card_id,
                                  request_type=RequestType.DELETE)

        plan, error = self.storage_provider.execute(request)

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

    # region convenience methods

    def archive_card(self, card_id: int = None, card_name: str = None,
                     request_user_id: int = None) -> None:
        cards = self.card_read(card_id, card_name, request_user_id)
        self.card_write(self.storage_provider.archived_list_id, cards[0], request_user_id)

    def get_cards_in_list(self, list_id: int, request_user_id: int) -> List[Card]:
        card_list = self.list_read(list_id=list_id, request_user_id=request_user_id)[0]
        return [self.card_read(card_id=card_id, request_user_id=request_user_id)[0] for card_id in card_list.cards]

    def get_archived_cards(self, request_user_id: int = None) -> List[Card]:
        return self.get_cards_in_list(self.storage_provider.archived_list_id, request_user_id)

    # end region


if __name__ == '__main__':
    model = Model("/Users/gleblinnik/Developer/isp/beb-manager/library/db.db")
    print(model.plan_write(1, 1, datetime.timedelta(days=5), datetime.datetime.fromtimestamp(100000)))
