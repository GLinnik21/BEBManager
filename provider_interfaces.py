from enum import Enum, unique
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from typing import Any


@unique
class RequestAccessType(Enum):
    READ = 1
    WRITE = 2
    DELETE = 3


class IProviderSubscriber(metaclass=ABCMeta):
    @abstractmethod
    def process(self, respond: Any, error: namedtuple) -> None:
        pass


class IProvider(metaclass=ABCMeta):
    @abstractmethod
    def execute(self, request: namedtuple, subscriber: IProviderSubscriber = None) -> None:
        pass
