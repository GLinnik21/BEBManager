from collections import namedtuple
from core.entity.domain_entites import UniversalContainer
from core.usecase.interfaces import IInputBoundary

BoardCreationRequest = namedtuple('BoardCreationRequest', ['name', 'uuid'])


class CreateBoardUseCase(IInputBoundary):

    def __init__(self, boards_repo=None):
        self.boards_data_repo = boards_repo

    def execute(self, request_model, output_port):
        if self.boards_data_repo is not None:
            board = UniversalContainer(name=request_model.name, unique_id=request_model.uuid)
            self.boards_data_repo.add_board(board)
