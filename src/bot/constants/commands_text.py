from enum import Enum


class CMD(Enum):
    CANCEL = "cancel"
    START = "start"
    CREATE_RECORD = "add_record"
    CREATE_STRATEGY = "set_strateg"
    CREATE_SCENARIO = "create_scenario"
    SCENARIOS_LIST = "get_my_scenarios"
