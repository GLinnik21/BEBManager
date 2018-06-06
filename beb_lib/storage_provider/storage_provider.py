from collections import namedtuple
from beb_lib import IProviderSubscriber, IProvider


class StorageProvider(IProvider):
    """
    Designed to create a kind of interlayer between the core and concrete DB implementation
    """
    def __init__(self):
        pass

    def execute(self, request: namedtuple, subscriber: IProviderSubscriber = None) -> None:
        pass
