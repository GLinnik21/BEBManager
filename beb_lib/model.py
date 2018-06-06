from collections import namedtuple
from beb_lib import IProviderSubscriber, IProvider


BoardDataRequest = namedtuple('BoardDataRequest', ['id', 'name', 'user', 'request_type'])
ListDataRequest = namedtuple('ListDataRequest', ['id', 'name', 'user', 'request_type'])
CardDataRequest = namedtuple('CardDataRequest',
                            ['id', 'name', 'user', 'request_type', 'description',
                             'expiration_date', 'priority', 'attachments',
                             'parent', 'children', 'tags',
                             'comments', 'list'])


class Model(IProvider):
    """
    Base mediator between all requests. It's created for future extensions.
    For now it processes only storage-related requests
    """
    storage_provider: IProvider

    def __init__(self, storage_provider: IProvider = None):
        """

        :param storage_provider: Instance of IProvider-compliant class that responsble for handling storage-related tasks
        """
        self.storage_provider = storage_provider

    def execute(self, request: namedtuple, subscriber: IProviderSubscriber = None) -> None:
        """

        :param request: Request DTO to process
        :param subscriber: Object of IProviderSubscriber-compliant class that is mean to process the respond to request
        """
        provider: IProvider = None

        if request.__name__ == 'BoardDataRequest' or\
                request.__name__ == 'ListDataRequest' or\
                request.__name__ == 'CardDataRequest':
            provider = self.storage_provider

        provider.execute(request, subscriber)
