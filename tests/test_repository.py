import pytest
from sqlalchemy import create_engine

from src.db.models import User, Scenario, UserScenario
from src.db.repository import create_user, get_user_by_chat, create_or_get_scenario, create_user_scenario, get_user_scenarios_by_chat


@pytest.fixture
def test_engine():
    engine = create_engine("sqlite:///:memory:")
    from src.db.models import BaseModel
    BaseModel.metadata.create_all(engine)
    yield engine
    BaseModel.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def override_engine(test_engine, monkeypatch):
    monkeypatch.setattr('src.db.repository.engine', test_engine)
    monkeypatch.setattr('src.db.models.engine', test_engine)


def test_create_user():
    user = create_user(123)
    assert user.chat_id == 123
    assert user.id is not None


def test_get_user_by_chat():
    create_user(456)
    user = get_user_by_chat(456)
    assert user is not None
    assert user.chat_id == 456


def test_create_or_get_scenario():
    scenario = create_or_get_scenario("New Scenario")
    assert scenario.name == "New Scenario"
    # Test getting existing
    scenario2 = create_or_get_scenario("New Scenario")
    assert scenario.id == scenario2.id


def test_create_user_scenario():
    user = create_user(789)
    scenario = create_or_get_scenario("User Scenario")
    user_scenario = create_user_scenario("User Scenario", 789)
    assert user_scenario.user_id == user.id
    assert user_scenario.scenario_id == scenario.id


def test_get_user_scenarios_by_chat():
    user = create_user(101)
    scenario1 = create_or_get_scenario("Scenario 1")
    scenario2 = create_or_get_scenario("Scenario 2")
    create_user_scenario("Scenario 1", 101)
    create_user_scenario("Scenario 2", 101)
    scenarios = list(get_user_scenarios_by_chat(101))
    assert len(scenarios) == 2