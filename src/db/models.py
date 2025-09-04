import os

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL)


class BaseModel(DeclarativeBase):
    pass


class User(BaseModel):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(unique=True)
    time_zone: Mapped[str | None]


class Scenario(BaseModel):
    __tablename__ = "scenarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)


class UserScenario(BaseModel):
    __tablename__ = "user_scenarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    allow_reminding: Mapped[bool]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    scenario_id: Mapped[int] = mapped_column(ForeignKey("scenarios.id"), unique=True)
    reminder_strategy_id: Mapped[int] = mapped_column(
        ForeignKey("reminder_strategies.id")
    )
    scenario: Mapped["Scenario"] = relationship(lazy="joined")


class ReminderStrategy(BaseModel):
    __tablename__ = "reminder_strategies"
    id: Mapped[int] = mapped_column(primary_key=True)
    module: Mapped[int] = mapped_column(nullable=False)
    shift: Mapped[int] = mapped_column(nullable=False)


class Parametr(BaseModel):
    __tablename__ = "parametrs"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    user_scenario_id: Mapped[int] = mapped_column(ForeignKey("user_scenarios.id"))
    default_value: Mapped[int | None]


class Record(BaseModel):
    __tablename__ = "records"
    id: Mapped[int] = mapped_column(primary_key=True)
    parameter_id: Mapped[int] = mapped_column(ForeignKey("parametrs.id"))
    value: Mapped[float]
    datetime: Mapped[DateTime] = mapped_column(DateTime(timezone=True))


# BaseModel.metadata.drop_all(engine)
BaseModel.metadata.create_all(engine)
