class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class AccessDeniedError(Error):

    def __init__(self, reason):
        super().__init__(reason)


class BoardDoesNotExistError(Error):

    def __init__(self, reason):
        super().__init__(reason)
