from collections import namedtuple
from core.usecase.interfaces import IInputBoundary

ListDeletionRequest = namedtuple('ListDeletionRequest', ['name', 'uuid'])


class ListCardsUseCase(IInputBoundary):

    def __init__(self, lists_repo=None):
        self.lists_data_repo = lists_repo

    def execute(self, request_model, output_port):
        if self.lists_data_repo is not None:
            self.lists_data_repo.delete_list(request_model.uuid)
