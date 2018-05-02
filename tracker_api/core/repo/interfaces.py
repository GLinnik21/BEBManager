from abc import ABCMeta, abstractmethod


class BoardRepo(metaclass=ABCMeta):

    @abstractmethod
    def get(self, board_id):
        pass

    @abstractmethod
    def set(self, board):
        pass
