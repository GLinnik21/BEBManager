from collections import namedtuple
from core.entity.domain_entites import UniversalContainer
from core.usecase.interfaces import IInputBoundary

ListCreationRequest = namedtuple('ListCreationRequest', ['name', 'uuid'])


class CreateListUseCase(IInputBoundary):

    def __init__(self):
        self.lists_data_repo = None

    def execute(self, request_model, output_port):
        if self.lists_data_repo is not None:
            board_list = UniversalContainer(request_model.name, unique_id=request_model.uuid)
            self.lists_data_repo.set(board_list)
