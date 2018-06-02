from provider_interfaces import *


BoardDataRequest = namedtuple('BoardDataRequest', ['name', 'user', 'access_type'])
ListDataRequest = namedtuple('ListDataRequest', ['name', 'user', 'access_type'])
CardDataRequest = namedtuple('CardDataRequest',
                            ['name', 'user', 'access_type', 'description',
                             'expiration_date', 'priority', 'attachments',
                             'parent', 'children', 'tags',
                             'comments', 'list'])


class Model(IProvider):
    storage_provider: IProvider

    def __init__(self):
        self.storage_provider = None
        self.subscribers = None

    def execute(self, request: namedtuple, subscriber: IProviderSubscriber = None) -> None:
        provider: IProvider = None

        if request.__name__ == 'BoardDataRequest' or\
                request.__name__ == 'ListDataRequest' or\
                request.__name__ == 'CardDataRequest':
            provider = self.storage_provider

        provider.execute(request, subscriber)
