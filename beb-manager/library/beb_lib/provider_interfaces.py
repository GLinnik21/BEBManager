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


class IProviderSubscriber(metaclass=ABCMeta):
    """
    Interface for entities that have to respond somehow to IProvider signals. This is needed to implement async
    requests.
    """

    @abstractmethod
    def process(self, respond: namedtuple, error: namedtuple = None) -> None:
        """

        :param respond: Object that IProvider could send (e.g. object fetched from the DB in response to request)
        :param error: Passed in case if shit happens
        """
        pass


class IProvider(metaclass=ABCMeta):
    """
    Interface for classes that are responsible for processing or mediating something
    """

    @abstractmethod
    def execute(self, request: namedtuple, subscriber: IProviderSubscriber = None) -> None:
        """
        This method is meant to be used for asynchronous calls
        :param request: Meant to use a simple DTO, defined in concrete IProvider implementation
         with the description of the request (use RequestType enum provided)
        :param subscriber: Optional object of IProviderSubscriber-compliant class that is meant to be passed through all
         IProvider chain to be called in response
        """
        pass

    @abstractmethod
    def sync_execute(self, request: namedtuple) -> (namedtuple, BaseError):
        """

        :param request: Meant to use a simple DTO, defined in concrete IProvider implementation
         with the description of the request (use RequestType enum provided)
        :return: Result of execution. Similar to 'process' method from 'IProviderSubscriber'.
        """
        pass
