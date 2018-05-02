from collections import namedtuple
from core.entity.domain_entites import UniversalContainer
from core.usecase.interfaces import IInputBoundary

BoardCreationRequest = namedtuple('BoardCreationRequest', ['name', 'uuid'])


class CreateBoardUseCase(IInputBoundary):

    def __init__(self):
        self.boards_data_repo = None

    def execute(self, request_model, output_port):
        if self.boards_data_repo is not None:
            board = UniversalContainer(request_model.name, unique_id=request_model.uuid)
            self.boards_data_repo.set(board)
