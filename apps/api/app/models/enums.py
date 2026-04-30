import enum


class EventType(enum.Enum):
    birthday = "birthday"
    wedding = "wedding"
    new_year = "new_year"
    other = "other"


class ItemPriority(enum.IntEnum):
    normal = 0
    high = 1
    must_have = 2
