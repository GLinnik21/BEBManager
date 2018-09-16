import datetime
from typing import List

from beb_lib.domain_entities.unique_object import UniqueObject


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
                 expiration_date: datetime.datetime = None,
                 priority: int = None,
                 children: List[int] = None,
                 tags: List[int] = None,
                 created: datetime = None,
                 last_modified: datetime = None,
                 plan: int = None
                 ):
        """

        :param name: Name of the card.
        :param unique_id: Unique identifier of card. If None is passed a new UUID would be generated
        :param user_id: The id of the user who has created this card
        :param assignee_id: The id of the user who the particular card was assigned
        :param description: Task description
        :param expiration_date: Date when the task should be done
        :param priority: Priority of the task. Recommended to use values from 1 to 100 or just predefined values from
        Priority enum
        :param children: Children cards ID's
        :param tags: Tags to sort card
        :param created: Date when the task was created
        :param last_modified: Date when the task was last edited
        :param plan: The id of plan instance that is used to create periodic tasks
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
        self.plan = plan

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @property
    def tags(self):
        return self._tags

    @property
    def children(self):
        return self._children


CARD_LIST_DEFAULTS = ['To Do',
                      'In Progress',
                      'Done']
