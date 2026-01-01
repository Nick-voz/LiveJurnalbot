from enum import IntEnum
from enum import auto

END = -1


class Scenario(IntEnum):
    NAME = auto()
    ADD_PARAMETERS = auto()
    PARAMETERS = auto()
    DENY = auto()


class ReminderStrategyStates(IntEnum):
    USER_SCENARIO = auto()
    MODULE = auto()
    SHIFT = auto()


class ParametrStates(IntEnum):
    USER_SCENARIO = auto()
    NAME = auto()
    DEFAULT_VALUE = auto()
    CONTINUE = auto()


class RecordStates(IntEnum):
    USER_SCENARIO = auto()
    PARAMETR = auto()
    VALUE = auto()


class Menu(IntEnum):
    CREATE_SCENARIO = auto()
    CHOOSING_OPTION = auto()


class ScenariosList(IntEnum):
    SCENARIO = auto()
    OPTION = auto()
    DELETE_CONFIRM = auto()
    RENAME = auto()
    PARAMETERS = auto()
