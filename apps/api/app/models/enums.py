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


class WishlistVisibility(enum.StrEnum):
    public = "public"  # discoverable on profile, indexable
    link_only = "link_only"  # accessible only via direct link, noindex
    private = "private"  # owner + invited emails only


class ReservationMode(enum.StrEnum):
    anonymous = "anonymous"  # anyone, including unauthenticated
    registered_only = "registered_only"  # registered users only
