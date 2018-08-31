from datetime import datetime
import enum
from enum import Enum
from typing import List


class UniqueObject:
    """
    Base class for all entities. It declares fields that every entity must have.
    Should be used only for subclassing, not for creating instances of this class
    """

    def __init__(self, name: str = None, unique_id: int = None):
        """

        :param name: Name
        :param unique_id: Unique identifier of object. If None is passed a new UUID would be generated
        """
        self.unique_id = unique_id
        self.name = name


class Tag(UniqueObject):
    """
    Tag is used to sort cards even from different lists
    """

    def __init__(self,
                 name: str,
                 unique_id: int = None,
                 color: int = None):
        """

        :param name: Name of the tag
        :param unique_id: Unique identifier of the tag. If None is passed a new UUID would be generated
        :param color: Optional color for tag. Should not be unique
        """
        super(Tag, self).__init__(name, unique_id)
        self.color = color


class Priority(enum.IntEnum):
    LOW = 1
    MEDIUM = 50
    HIGH = 100


@enum.unique
class AccessType(enum.Flag):
    """
    Members of this class could be combined using the bitwise operators (&, |, ^)
    Used to determine what type of access user may have to board.
    Use AccessType Flag enum combinations (e.g. AccessType.READ | AccessType.WRITE) for this.
    Pass AccessType.NONE or AccessType.READ & AccessType.WRITE to ban access for user to board
    """
    READ = enum.auto()
    WRITE = enum.auto()
    READ_WRITE = READ | WRITE
    NONE = READ & WRITE


class Card(UniqueObject):
    """
    Main entity for creating a task. One card is meant to represent one task.
    """

    def __init__(self,
                 name: str,
                 unique_id: int = None,
                 user_id: int = None,
                 assignee_id: int = None,
                 description: str = None,
                 expiration_date: datetime = None,
                 priority: int = None,
                 children: List[int] = None,
                 tags: List[int] = None,
                 created: datetime = None,
                 last_modified: datetime = None,
                 ):
        """

        :param name: Name of the card.
        :param unique_id: Unique identifier of card. If None is passed a new UUID would be generated
        :param user_id: The id of the user who has created with card
        :param assignee_id: The id of the user who the particular card was assigned
        :param description: Task description
        :param expiration_date: Date when the task should be done
        :param priority: Priority of the task. Recommended to use values from 1 to 100 or just predefined values from
        Priority enum
        :param children: Children cards ID's
        :param tags: Tags to sort card
        :param created: Date when the task was created
        :param last_modified: Date when the task was last edited
        """
        super(Card, self).__init__(name, unique_id)
        self.user_id = user_id
        self.assignee_id = assignee_id
        self.description = description
        self.expiration_date = expiration_date
        self.priority = priority
        self._children = children
        self._tags = tags
        self.created = created
        self.last_modified = last_modified

    @property
    def tags(self):
        return self._tags

    @property
    def children(self):
        return self._children


CARD_LIST_DEFAULTS = ['To Do',
                      'In Progress',
                      'Done']


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
