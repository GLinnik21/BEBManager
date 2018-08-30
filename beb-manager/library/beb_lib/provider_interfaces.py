from enum import Enum, unique, auto
from abc import ABCMeta, abstractmethod
from collections import namedtuple


@unique
class RequestType(Enum):
    READ = auto()
    WRITE = auto()
    DELETE = auto()


REQUEST_BASE_FIELDS = ['request_id', 'request_type']
REQUEST_ACCESS_FIELDS = REQUEST_BASE_FIELDS + ['request_user_id']
RESPONSE_BASE_FIELDS = ['request_id']


BaseError = namedtuple('BaseError', ['code', 'description'])


class IProvider(metaclass=ABCMeta):
    """
    Interface for classes that are responsible for processing or mediating something
    """

    @abstractmethod
    def execute(self, request: namedtuple) -> (namedtuple, BaseError):
        """

        :param request: Meant to use a simple DTO, defined in concrete IProvider implementation
         with the description of the request (use RequestType enum provided)
        :return: Result of execution.
        """
        pass
