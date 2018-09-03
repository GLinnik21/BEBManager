from beb_lib.domain_entities.unique_object import UniqueObject


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
