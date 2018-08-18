from collections import namedtuple
from beb_lib import (IProviderSubscriber,
                     IProvider)
from .storage_provider_protocol import IStorageProviderProtocol


class StorageProvider(IProvider, IStorageProviderProtocol):
    """
    Designed to create a kind of interlayer between the core and concrete DB implementation
    """

    def __init__(self, path_to_db: str):
        pass

    def open(self) -> None:
        pass

    def close(self) -> None:
        pass

    def execute(self, request: namedtuple, subscriber: IProviderSubscriber = None) -> None:
        pass
