from abc import ABCMeta, abstractmethod


class BoardsRepo(metaclass=ABCMeta):

    @abstractmethod
    def list_boards(self):
        pass

    @abstractmethod
    def add_board(self, board):
        pass

    @abstractmethod
    def delete_board(self, board_id):
        pass

    @abstractmethod
    def modify_board(self, board):
        pass


class ListsRepo(metaclass=ABCMeta):

    @abstractmethod
    def list_lists(self, board_id):
        pass

    @abstractmethod
    def add_list(self, my_list, board_id):
        pass

    @abstractmethod
    def delete_list(self, list_id):
        pass

    @abstractmethod
    def modify_list(self, my_list):
        pass


class CardsRepo(metaclass=ABCMeta):

    @abstractmethod
    def list_cards(self, list_id):
        pass

    @abstractmethod
    def add_card(self, card, list_id):
        pass

    @abstractmethod
    def delete_card(self, card_id):
        pass

    @abstractmethod
    def modify_card(self, card):
        pass

