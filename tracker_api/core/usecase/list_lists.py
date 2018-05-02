from collections import namedtuple
from core.usecase.interfaces import IInputBoundary

ListListsRequest = namedtuple('ListCardsRequest', ['board_uuid'])
ListListsResponseListItem = namedtuple('ListCardsResponseListItem', ['name', 'uuid'])


class ListListsUseCase(IInputBoundary):

    def __init__(self, lists_repo=None):
        self.lists_data_repo = lists_repo

    def execute(self, request_model, output_port):
        if self.lists_data_repo is not None:
            lists = self.lists_data_repo.list_lists(request_model.board_uuid)

            response = []

            for my_list in lists:
                response.append(ListListsResponseListItem(name=my_list.name, uuid=my_list.unique_identifier))

            output_port.present(response)
