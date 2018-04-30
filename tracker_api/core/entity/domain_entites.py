import uuid
import copy


class UniqueObject:
    def __init__(self, name=None, unique_id=None):
        self._unique_identifier = (unique_id is None and uuid.uuid4()) or \
                                  ((unique_id is uuid and copy.deepcopy(unique_id)) or uuid.UUID(unique_id))
        self.name = name


class Tag(UniqueObject):
    def __init__(self, name, color, **kwargs):
        super(Tag, self).__init__(name, kwargs.get('unique_id', None))
        self.color = color


class Card(UniqueObject):
    def __init__(self, name, **kwargs):
        """
        :param kwargs:
        """
        super(Card, self).__init__(name, kwargs.get('unique_id', None))
        self.description = kwargs.get('description', None)
        self.expiration_date = kwargs.get('expiration_date', None)
        self.priority = kwargs.get('priority', None)
        self._attachments = kwargs.get('attachments', [])
        self.parent = kwargs.get('parent', None)
        self._children = kwargs.get('children', [])
        self._tags = kwargs.get('tags', [])
        self._comments = kwargs.get('comments', [])

    @property
    def children(self):
        return self._children

    @property
    def attachments(self):
        return self._attachments

    @property
    def tags(self):
        return self._tags

    @property
    def comments(self):
        return self._comments


class UniversalContainer(UniqueObject):
    def __init__(self, name, **kwargs):
        super(UniversalContainer, self).__init__(name, kwargs.get('unique_id', None))
        self._unique_objects = kwargs.get('unique_objects', [])

    @property
    def unique_objects(self):
        return self._unique_objects
