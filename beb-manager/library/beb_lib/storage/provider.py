import enum
from collections import namedtuple
from peewee import SqliteDatabase

from beb_lib.storage.access_validator import remove_right, add_right
from beb_lib.provider_interfaces import RESPONSE_BASE_FIELDS, IProvider, BaseError, RequestType
from beb_lib.storage.provider_protocol import IStorageProviderProtocol
from beb_lib.storage.models import (BoardModel,
                                    CardListModel,
                                    TagModel,
                                    CardModel,
                                    TagCard,
                                    ParentChild,
                                    CardUserAccess,
                                    CardListUserAccess,
                                    BoardUserAccess,
                                    DATABASE_PROXY,
                                    PlanModel
                                    )
from beb_lib.storage.provider_requests import (BoardDataRequest,
                                               CardDataRequest,
                                               AddAccessRightRequest,
                                               RemoveAccessRightRequest,
                                               ListDataRequest,
                                               TagDataRequest,
                                               PlanDataRequest
                                               )

BoardDataResponse = namedtuple('BoardDataResponse', RESPONSE_BASE_FIELDS + ['boards'])
ListDataResponse = namedtuple('ListDataResponse', RESPONSE_BASE_FIELDS + ['lists'])
CardDataResponse = namedtuple('CardDataResponse', RESPONSE_BASE_FIELDS + ['cards'])
TagDataResponse = namedtuple('TagDataResponse', RESPONSE_BASE_FIELDS + ['tags'])
PlanDataResponse = namedtuple('PlanDataResponse', RESPONSE_BASE_FIELDS + ['plan'])


@enum.unique
class StorageProviderErrors(enum.IntEnum):
    INVALID_REQUEST = enum.auto()
    REQUEST_TYPE_NOT_SPECIFIED = enum.auto()
    ACCESS_DENIED = enum.auto()
    BOARD_DOES_NOT_EXIST = enum.auto()
    LIST_DOES_NOT_EXIST = enum.auto()
    CARD_DOES_NOT_EXIST = enum.auto()
    TAG_DOES_NOT_EXIST = enum.auto()
    PLAN_DOES_NOT_EXIST = enum.auto()


class StorageProvider(IProvider, IStorageProviderProtocol):
    """
    Designed to create a kind of interlayer between the core and concrete DB implementation
    """

    def __init__(self, path_to_db: str):
        self.database_path = path_to_db
        self.database = SqliteDatabase(path_to_db)
        self.is_connected = False
        self.archived_list_id = None
        DATABASE_PROXY.initialize(self.database)
        # To prevent import cycle
        from beb_lib.storage.processors.board_processor import process_board_call
        from beb_lib.storage.processors.card_processor import process_card_call
        from beb_lib.storage.processors.list_processor import process_list_call
        from beb_lib.storage.processors.tag_processor import process_tag_call
        from beb_lib.storage.processors.plan_processor import process_plan_call

        self.handler_map = {
            BoardDataRequest: lambda request: process_board_call(request),
            ListDataRequest: lambda request: process_list_call(request),
            CardDataRequest: lambda request: process_card_call(request),
            TagDataRequest: lambda request: process_tag_call(request),
            PlanDataRequest: lambda request: process_plan_call(request),
            AddAccessRightRequest: lambda request: add_right(request.object_type, request.object_id,
                                                             request.user_id, request.access_type),
            RemoveAccessRightRequest: lambda request: remove_right(request.object_type, request.object_id,
                                                                   request.user_id, request.access_type)
        }

    def open(self) -> None:
        if not self.is_connected:
            self.database.connect()
            self.is_connected = True
        self.database.create_tables([BoardModel,
                                     CardListModel,
                                     TagModel,
                                     CardModel,
                                     TagCard,
                                     ParentChild,
                                     CardUserAccess,
                                     CardListUserAccess,
                                     BoardUserAccess,
                                     PlanModel])
        self.archived_list_id = CardListModel.get_or_create(name='Archived')[0].id

    def close(self) -> None:
        self.database.close()
        self.is_connected = False

    def execute(self, request: namedtuple) -> (namedtuple, BaseError):
        if type(request.request_type) is not RequestType:
            return None, BaseError(code=StorageProviderErrors.REQUEST_TYPE_NOT_SPECIFIED,
                                   description='Request type is not specified')

        handler = self.handler_map[type(request)]

        if handler is None:
            return None, BaseError(code=StorageProviderErrors.INVALID_REQUEST,
                                   description='This request cannot be handled by this provider')

        return handler(request)
