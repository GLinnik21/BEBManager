from collections import namedtuple
from threading import Thread

from beb_lib import (IProviderSubscriber,
                     IProvider,
                     BaseError)

from beb_lib.storage import (StorageProvider,
                             BoardDataRequest,
                             CardDataRequest,
                             ListDataRequest,
                             AddAccessRightRequest,
                             RemoveAccessRightRequest)


class Model(IProvider):
    """
    Base mediator between all requests. It's created for future extensions.
    For now it processes only storage-related requests
    """

    storage_provider: StorageProvider

    def __init__(self, storage_provider: StorageProvider):
        """

        :param storage_provider: Instance of IProvider-compliant class that responsible for handling storage-related
        tasks
        """
        self.storage_provider = storage_provider
        self.storage_provider.open()

    def execute(self, request: namedtuple, subscriber: IProviderSubscriber = None) -> None:
        """

        :param request: Request DTO to process
        :param subscriber: Object of IProviderSubscriber-compliant class that is mean to process the respond to request
        """

        t = Thread(target=self._async_execute, args=(request, subscriber,))
        t.start()

    def sync_execute(self, request: namedtuple) -> (namedtuple, BaseError):
        self._get_provider(request).sync_execute(request)

    def _get_provider(self, request: namedtuple) -> IProvider:
        provider: IProvider = None

        request_name = type(request).__name__

        if request_name == BoardDataRequest.__name__ or \
                request_name == ListDataRequest.__name__ or \
                request_name == CardDataRequest.__name__ or \
                request_name == AddAccessRightRequest.__name__ or \
                request_name == RemoveAccessRightRequest.__name__:
            provider = self.storage_provider

        return provider

    def _async_execute(self, request: namedtuple, subscriber: IProviderSubscriber = None) -> None:
        provider: IProvider = self._get_provider(request)
        provider.execute(request, subscriber)


# if __name__ == '__main__': pass
