from typing import Iterable

from sqlalchemy import Select
from sqlalchemy.orm import Session

from src.db.models import Scenario
from src.db.models import User
from src.db.models import UserScenario
from src.db.models import engine


def get_user_by_chat(chat_id: int) -> User:
    selector = Select(User).where(User.chat_id == chat_id)
    with Session(engine) as s:
        user = s.scalars(selector).one()
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


def get_user_scenario_by_name(name, chat_id) -> UserScenario:
    user = get_user_by_chat(chat_id)
    scenario = find_scenario_by_name(name)
    if scenario is None:
        raise RuntimeError()

    selector = (
        Select(UserScenario)
        .where(UserScenario.user_id == user.id)
        .where(UserScenario.scenario_id == scenario.id)
    )

    with Session(engine) as s:
        user_scenario = s.scalars(selector).one()

    return user_scenario


def create_user_scenario(name: str, chat_id: int) -> UserScenario:
    scenario = create_or_get_scenario(name)
    user = get_user_by_chat(chat_id)

    user_scenario = UserScenario(scenario_id=scenario.id, user_id=user.id)

    with Session(engine) as s:
        s.add(user_scenario)
        s.commit()


def get_user_scenarios_by_chat(chat_id: int) -> Iterable["UserScenario"]:
    user = get_user_by_chat(chat_id)
    selector = Select(UserScenario).where(UserScenario.user_id == user.id)

    with Session(engine) as s:
        scenarios = s.scalars(selector).all()

    return scenarios
