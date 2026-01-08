from typing import Iterable

from sqlalchemy import Select
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from src.db.models import Parameter
from src.db.models import Record
from src.db.models import ReminderStrategy
from src.db.models import Scenario
from src.db.models import User
from src.db.models import UserScenario
from src.db.models import Value
from src.db.models import engine


def create_user(chat_id) -> User:
    user = User(chat_id=chat_id)
    with Session(engine) as s:
        s.add(user)
        s.commit()
        s.refresh(user)
    return user


def get_user_by_chat(chat_id: int) -> User | None:
    selector = Select(User).where(User.chat_id == chat_id)
    with Session(engine) as s:
        user = s.scalars(selector).one_or_none()
    return user


def find_scenario_by_name(name: str) -> Scenario | None:
    selector = Select(Scenario).where(Scenario.name == name)
    with Session(engine) as s:
        scenario = s.scalars(selector).one_or_none()
    return scenario


def create_or_get_scenario(name: str) -> Scenario:
    scenario = find_scenario_by_name(name)
    if scenario is not None:
        return scenario

    scenario = Scenario(name=name)
    with Session(engine) as s:
        s.add(scenario)
        s.commit()
        s.refresh(scenario)

    return scenario


def find_user_scenario_by_name(name, chat_id) -> UserScenario:
    user = get_user_by_chat(chat_id)
    scenario = find_scenario_by_name(name)

    if scenario is None:
        return

    selector = (
        Select(UserScenario)
        .where(UserScenario.user_id == user.id)
        .where(UserScenario.scenario_id == scenario.id)
    )

    with Session(engine) as s:
        user_scenario = s.scalars(selector).one_or_none()

    return user_scenario


def create_user_scenario(name: str, chat_id: int) -> UserScenario:
    user_scenario = find_user_scenario_by_name(name, chat_id)
    if user_scenario is not None:
        return user_scenario

    scenario = create_or_get_scenario(name)
    user = get_user_by_chat(chat_id)

    user_scenario = UserScenario(
        scenario_id=scenario.id, user_id=user.id, allow_reminding=False
    )

    with Session(engine) as s:
        s.add(user_scenario)
        s.commit()
        s.refresh(user_scenario)

    return user_scenario


def get_user_scenarios_by_chat(chat_id: int) -> Iterable["UserScenario"]:
    user = get_user_by_chat(chat_id)
    selector = Select(UserScenario).where(UserScenario.user_id == user.id)

    with Session(engine) as s:
        scenarios = s.scalars(selector).all()

    return scenarios


def get_user_scenario_by_id(_id: int) -> UserScenario:
    selector = Select(UserScenario).where(UserScenario.id == _id)

    with Session(engine) as s:
        scenario = s.scalars(selector).one()

    return scenario


def create_reminder_strategy(user_scenario: UserScenario) -> ReminderStrategy:
    strategy = ReminderStrategy()
    user_scenario.reminder_strategy = strategy
    with Session(engine) as s:
        s.add_all((strategy, user_scenario))
        user_scenario.reminder_strategy = strategy
        s.commit()

    return find_or_create_reminder_strategy(user_scenario)


def find_or_create_reminder_strategy(user_scenario: UserScenario) -> ReminderStrategy:
    selector = (
        Select(ReminderStrategy)
        .join(UserScenario)
        .where(UserScenario.reminder_strategy_id == ReminderStrategy.id)
        .where(UserScenario.id == user_scenario.id)
    )
    with Session(engine) as s:
        strategy = s.scalars(selector).one_or_none()

    if strategy is None:
        return create_reminder_strategy(user_scenario)

    return strategy


def create_parameter(user_scenario: UserScenario, name: str) -> UserScenario:
    parameter = Parameter(name=name, user_scenario_id=user_scenario.id)
    with Session(engine) as s:
        s.add(parameter)
        s.commit()


def find_or_create_parameter(user_scenario: UserScenario, name: str) -> Parameter:
    selector = (
        Select(Parameter)
        .join(UserScenario)
        .where(Parameter.user_scenario_id == UserScenario.id)
        .where(Parameter.name == name)
    )
    with Session(engine) as s:
        parameter = s.scalars(selector).one_or_none()

    if parameter is None:
        create_parameter(user_scenario, name)
        return find_or_create_parameter(user_scenario, name)

    return parameter


def get_user_scenario_parameters(user_scenario: UserScenario) -> Iterable[Parameter]:
    selector = Select(Parameter).where(Parameter.user_scenario_id == user_scenario.id)

    with Session(engine) as s:
        parameters = s.scalars(selector).all()

    return parameters


def update_user_scenario_name(user_scenario_id: int, new_name: str) -> None:
    user_scenario = get_user_scenario_by_id(user_scenario_id)
    with Session(engine) as s:
        s.add(user_scenario)
        user_scenario.scenario.name = new_name
        s.commit()


def delete_user_scenario_by_id(scenario_id):
    selector = Select(UserScenario).where(UserScenario.id == scenario_id)
    with Session(engine) as s:
        user_scenario = s.scalars(selector).one_or_none()
        if user_scenario:
            s.delete(user_scenario)
            s.commit()


def update_parameter_default_value(parameter: Parameter):
    with Session(engine) as s:
        s.add(parameter)
        s.commit()


def save_record(record: Record) -> Record:
    with Session(engine) as s:
        s.add(record)
        s.commit()
        s.refresh(record)
    return record


def save_value(value: Value) -> Value:
    with Session(engine) as s:
        s.add(value)
        s.commit()
        s.refresh(value)
    return value


def update_reminder_strategy(strategy: ReminderStrategy):
    with Session(engine) as s:
        s.add(strategy)
        s.commit()


def get_scenario_values(user_scenario_id: int) -> list[Value]:
    selector = (
        Select(Value)
        .join(Value.parameter)
        .join(Value.record)
        .where(Parameter.user_scenario_id == user_scenario_id)
        .options(joinedload(Value.parameter), joinedload(Value.record))
    )
    with Session(engine) as s:
        return s.scalars(selector).all()
