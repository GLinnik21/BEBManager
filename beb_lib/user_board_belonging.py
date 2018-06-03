from beb_lib import User, Board
from enum import Flag, unique, auto


@unique
class AccessType(Flag):
    """
    Members of this class could be combined using the bitwise operators (&, |, ^, ~)
    """
    READ = auto()
    WRITE = auto()
    READ_WRITE = READ | WRITE
    NONE = READ & WRITE


class UserBoardBelonging:
    """
    Used to determine how board belongs to user
    """
    board: Board
    user: User

    def __init__(self, user: User, board: Board, access_type: AccessType = AccessType.READ | AccessType.WRITE) -> None:
        """

        :param access_type: Used to determine what type of access user may have to board.
        Use AccessType Flag enum combinations (e.g. AccessType.READ | AccessType.WRITE) for this.
        Pass AccessType.NONE or AccessType.READ & AccessType.WRITE to ban access for user to board
        :param user: User who this board related somehow
        :param board: Board that is related to the user
        """
        self.user = user
        self.board = board
        self.access_type = access_type
