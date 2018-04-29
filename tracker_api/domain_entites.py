import uuid
import copy


class UniqueObject:
    def __init__(self, unique_id=None, name=None):
        self._unique_identifier = (unique_id is None and uuid.uuid4()) or \
                                  ((unique_id is uuid and copy.deepcopy(unique_id)) or uuid.UUID(unique_id))
        self.name = name


class Tag(UniqueObject):
    def __init__(self, name, color, **kwargs):
        super(Tag, self).__init__(kwargs.get('unique_id', None), name)


class Card(UniqueObject):
    def __init__(self, name, **kwargs):
        """
        :param kwargs:
        """
        super(Card, self).__init__(kwargs.get('unique_id', None), name)
        self.description = kwargs.get('description', None)
        self.expiration_date = kwargs.get('expiration_date', None)
        self.priority = kwargs.get('priority', None)
        self.attachments = kwargs.get('attachments', [])
        self.parent = kwargs.get('parent', None)
        self.children = kwargs.get('children', [])
        self.tags = kwargs.get('tags', [])
        self.comments = kwargs.get('comments', [])


class List(UniqueObject):
    def __init__(self, name, **kwargs):
        super(List, self).__init__(kwargs.get('unique_id', None), name)
        self.cards = kwargs.get('cards', [])


class Board(UniqueObject):
    def __init__(self, name, **kwargs):
        super(Board, self).__init__(kwargs.get('unique_id', None), name)
        self.lists = kwargs.get('lists', [])
