from typing import List

from beb_lib.domain_entities.card import Card
from beb_lib.domain_entities.unique_object import UniqueObject


class Board(UniqueObject):
    """
    Used to organize cards with tasks into ordered list
    """
    _lists: List[Card]

    def __init__(self,
                 name: str,
                 unique_id: int = None,
                 lists: List[int] = None):
        """

        :param name: Name of the list
        :param unique_id: Unique identifier of card. If None is passed a new UUID would be generated
        :param lists: Unique lists
        """
        super(Board, self).__init__(name, unique_id)
        self._lists = lists

    @property
    def cards(self):
        return self._lists
