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
