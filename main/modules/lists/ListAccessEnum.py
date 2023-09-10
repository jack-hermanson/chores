from enum import IntEnum


class ListAccessEnum(IntEnum):
    READONLY = 0
    MEMBER = 1
    ADMIN = 2
    OWNER = 3
