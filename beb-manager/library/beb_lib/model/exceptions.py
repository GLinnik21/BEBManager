"""
    This package contains exceptions module
"""
class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class AccessDeniedError(Error):

    def __init__(self, reason):
        super().__init__(reason)


class UniqueObjectDoesNotExistError(Error):

    def __init__(self, reason):
        super().__init__(reason)


class BoardDoesNotExistError(UniqueObjectDoesNotExistError):

    def __init__(self, reason):
        super().__init__(reason)


class ListDoesNotExistError(UniqueObjectDoesNotExistError):

    def __init__(self, reason):
        super().__init__(reason)


class CardDoesNotExistError(UniqueObjectDoesNotExistError):

    def __init__(self, reason):
        super().__init__(reason)


class TagDoesNotExistError(UniqueObjectDoesNotExistError):

    def __init__(self, reason):
        super().__init__(reason)


class PlanDoesNotExistError(UniqueObjectDoesNotExistError):

    def __init__(self, reason):
        super().__init__(reason)
