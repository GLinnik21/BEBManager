from collections import namedtuple
from core.entity.domain_entites import UniversalContainer
from core.usecase.interfaces import IInputBoundary

ListCreationRequest = namedtuple('ListCreationRequest', ['name', 'uuid', 'board_uuid'])


class CreateListUseCase(IInputBoundary):

    def __init__(self, lists_repo=None):
        self.lists_data_repo = lists_repo

    def execute(self, request_model, output_port):
        if self.lists_data_repo is not None:
            my_list = UniversalContainer(name=request_model.name, unique_id=request_model.uuid)
            self.lists_data_repo.add_list(my_list, request_model.board_uuid)
