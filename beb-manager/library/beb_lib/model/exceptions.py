class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class AccessDeniedError(Error):

    def __init__(self, reason):
        super().__init__(reason)


class BoardDoesNotExistError(Error):

    def __init__(self, reason):
        super().__init__(reason)


class ListDoesNotExistError(Error):

    def __init__(self, reason):
        super().__init__(reason)


class CardDoesNotExistError(Error):

    def __init__(self, reason):
        super().__init__(reason)


class TagDoesNotExistError(Error):

    def __init__(self, reason):
        super().__init__(reason)


class PlanDoesNotExistError(Error):

    def __init__(self, reason):
        super().__init__(reason)
