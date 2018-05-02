from collections import namedtuple
from core.usecase.interfaces import IInputBoundary

ListCardsRequest = namedtuple('ListCardsRequest', ['list_uuid'])
ListCardsResponseListItem = namedtuple('ListCardsResponseListItem', ['name', 'uuid'])


class ListCardsUseCase(IInputBoundary):

    def __init__(self, cards_repo=None):
        self.cards_data_repo = cards_repo

    def execute(self, request_model, output_port):
        if self.cards_data_repo is not None:
            cards = self.cards_data_repo.list_cards(request_model.list_uuid)

            response = []

            for card in cards:
                response.append(ListCardsResponseListItem(name=card.name, uuid=card.unique_identifier))

            output_port.present(response)
