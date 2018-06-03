from enum import Enum, unique, auto
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from typing import Any


@unique
class RequestType(Enum):
    READ = auto()
    WRITE = auto()
    DELETE = auto()


class IProviderSubscriber(metaclass=ABCMeta):
    """
    Interface for entities that have to respond somehow to IProvider signals. This is needed to implement async requests
    in the future.
    """
    @abstractmethod
    def process(self, respond: Any, error: namedtuple = None) -> None:
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

        :param request: Meant to use a simple DTO, defined in concrete IProvider implementation
         with the description of the request (use RequestType enum provided)
        :param subscriber: Optional object of IProviderSubscriber-compliant class that is meant to be passed through all
         IProvider chain to be called in response
        """
        pass
