from collections import namedtuple
from core.usecase.interfaces import IInputBoundary

CardDeletionRequest = namedtuple('CardDeletionRequest', ['name', 'uuid'])


class ListCardsUseCase(IInputBoundary):

    def __init__(self, cards_repo=None):
        self.cards_data_repo = cards_repo

    def execute(self, request_model, output_port):
        if self.cards_data_repo is not None:
            self.cards_data_repo.delete_card(request_model.uuid)
