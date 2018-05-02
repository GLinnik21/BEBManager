from collections import namedtuple
from core.usecase.interfaces import IInputBoundary

ListBoardsResponseListItem = namedtuple('ListBoardsResponseListItem', ['name', 'uuid'])


class ListCardsUseCase(IInputBoundary):

    def __init__(self, boards_repo=None):
        self.boards_data_repo = boards_repo

    def execute(self, request_model, output_port):
        if self.boards_data_repo is not None:
            boards = self.boards_data_repo.list_cards(request_model.list_uuid)

            response = []

            for board in boards:
                response.append(ListBoardsResponseListItem(name=board.name, uuid=board.unique_identifier))

            output_port.present(response)
