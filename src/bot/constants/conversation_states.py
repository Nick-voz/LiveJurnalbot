from enum import IntEnum
from enum import auto


class Scenario(IntEnum):
    NAME = auto()


class ReminderStrategyStates(IntEnum):
    USER_SCENARIO = auto()
    MODULE = auto()
    SHIFT = auto()
