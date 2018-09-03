from typing import List

from beb_lib.domain_entities.card import Card
from beb_lib.domain_entities.unique_object import UniqueObject


class CardsList(UniqueObject):
    """
    Used to organize cards with tasks into ordered list
    """
    _cards: List[Card]

    def __init__(self,
                 name: str,
                 unique_id: int = None,
                 cards: List[int] = None):
        """

        :param name: Name of the list
        :param unique_id: Unique identifier of card. If None is passed a new UUID would be generated
        :param cards: Unique cards
        """
        super(CardsList, self).__init__(name, unique_id)
        self._cards = cards

    @property
    def cards(self):
        return self._cards

