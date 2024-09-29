from enum import Enum


def choices_from_enum(cls: Enum):
    return [(item.name, item.value) for item in cls]


class DjangoEnum(Enum):
    @classmethod
    def choices(cls):
        return choices_from_enum(cls)


class MarketType(Enum):
    NIFTY = 'NIFTY'
    BANKNIFTY = 'BANKNIFTY'
