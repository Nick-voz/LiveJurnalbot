from typing import Iterable

from sqlalchemy import Select
from sqlalchemy.orm import Session

from src.db.models import Parametr
from src.db.models import ReminderStrategy
from src.db.models import Scenario
from src.db.models import User
from src.db.models import UserScenario
from src.db.models import engine


def create_user(chat_id) -> User:
    user = User(chat_id=chat_id)
    with Session(engine) as s:
        s.add(user)
        s.commit()


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

    scenario = find_scenario_by_name(name)
    if scenario is None:
        raise RuntimeError(f"something went wrong with scenario namede: {name}")

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

    user_scenario = UserScenario(scenario_id=scenario.id, user_id=user.id)
    user_scenario.allow_reminding = False
    user_scenario.reminder_strategy_id = 1

    with Session(engine) as s:
        s.add(user_scenario)
        s.commit()

    return find_user_scenario_by_name(name, chat_id)


def get_user_scenarios_by_chat(chat_id: int) -> Iterable["UserScenario"]:
    user = get_user_by_chat(chat_id)
    selector = Select(UserScenario).where(UserScenario.user_id == user.id)

    with Session(engine) as s:
        scenarios = s.scalars(selector).all()

    return scenarios


def create_reminder_strategy(user_scenario: UserScenario) -> ReminderStrategy:
    strategy = ReminderStrategy()
    with Session(engine) as s:
        s.add(strategy)
        user_scenario.reminder_strategy_id = strategy.id
        s.commit()


def find_or_create_reminder_strategy(user_scenario: UserScenario) -> ReminderStrategy:
    selector = (
        Select(ReminderStrategy)
        .join(UserScenario)
        .where(UserScenario.reminder_strategy_id == ReminderStrategy.id)
    )
    with Session(engine) as s:
        strategy = s.scalars(selector).one_or_none()

    if strategy is None:
        create_reminder_strategy(user_scenario)
        return find_or_create_reminder_strategy(user_scenario)

    return strategy


def create_parametr(user_scenario: UserScenario, name: str) -> UserScenario:
    parametr = Parametr(name=name, user_scenario_id=user_scenario.id)
    with Session(engine) as s:
        s.add(parametr)
        s.commit()


def find_or_create_parametr(user_scenario: UserScenario, name: str) -> Parametr:
    selector = (
        Select(Parametr)
        .join(UserScenario)
        .where(Parametr.user_scenario_id == UserScenario.id)
        .where(Parametr.name == name)
    )
    with Session(engine) as s:
        parametr = s.scalars(selector).one_or_none()

    if parametr is None:
        create_parametr(user_scenario, name)
        return find_or_create_parametr(user_scenario, name)

    return parametr


def get_user_scenario_parametrs(user_scenario: UserScenario) -> Iterable[Parametr]:
    selector = Select(Parametr).where(Parametr.user_scenario_id == user_scenario.id)

    with Session(engine) as s:
        parametrs = s.scalars(selector).all()

    return parametrs
