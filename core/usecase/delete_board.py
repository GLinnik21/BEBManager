from collections import namedtuple
from core.usecase.interfaces import IInputBoundary

BoardDeletionRequest = namedtuple('BoardDeletionRequest', ['name', 'uuid'])


class ListCardsUseCase(IInputBoundary):

    def __init__(self, boards_repo=None):
        self.boards_data_repo = boards_repo

    def execute(self, request_model, output_port):
        if self.boards_data_repo is not None:
            self.boards_data_repo.delete_board(request_model.uuid)
