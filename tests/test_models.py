import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.db.models import BaseModel, User, Scenario


@pytest.fixture
def test_engine():
    engine = create_engine("sqlite:///:memory:")
    BaseModel.metadata.create_all(engine)
    yield engine
    BaseModel.metadata.drop_all(engine)


@pytest.fixture
def test_session(test_engine):
    with Session(test_engine) as session:
        yield session


def test_create_user(test_session):
    user = User(chat_id=123)
    test_session.add(user)
    test_session.commit()
    assert user.id is not None
    assert user.chat_id == 123


def test_create_scenario(test_session):
    scenario = Scenario(name="Test Scenario")
    test_session.add(scenario)
    test_session.commit()
    assert scenario.id is not None
    assert scenario.name == "Test Scenario"
