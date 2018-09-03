import enum


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
