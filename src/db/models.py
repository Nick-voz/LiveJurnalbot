import os

from datetime import datetime
from datetime import timezone
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
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
    chat_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    time_zone: Mapped[str | None]
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class Scenario(BaseModel):
    __tablename__ = "scenarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    user_scenarios: Mapped[list["UserScenario"]] = relationship(
        back_populates="scenario"
    )


# pylint: disable={E1136} # unsubscriptable-object for Mapped[int] IDK why
class UserScenario(BaseModel):
    __tablename__ = "user_scenarios"
    __table_args__ = (UniqueConstraint("user_id", "scenario_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    allow_reminding: Mapped[bool] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    scenario_id: Mapped[int] = mapped_column(
        ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False
    )
    reminder_strategy_id: Mapped[int] = mapped_column(
        ForeignKey("reminder_strategies.id"), nullable=True
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    scenario: Mapped["Scenario"] = relationship(
        back_populates="user_scenarios", lazy="joined"
    )
    reminder_strategy: Mapped["ReminderStrategy"] = relationship(
        back_populates="user_scenarios", lazy="joined"
    )
    parameters: Mapped[list["Parameter"]] = relationship(back_populates="user_scenario")


class ReminderStrategy(BaseModel):
    __tablename__ = "reminder_strategies"
    id: Mapped[int] = mapped_column(primary_key=True)
    module: Mapped[int] = mapped_column(nullable=False, default=0)
    shift: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    user_scenarios: Mapped[list["UserScenario"]] = relationship(
        back_populates="reminder_strategy"
    )


class Parameter(BaseModel):
    __tablename__ = "parameters"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    user_scenario_id: Mapped[int] = mapped_column(
        ForeignKey("user_scenarios.id", ondelete="CASCADE"), nullable=False
    )
    default_value: Mapped[float | None]
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    user_scenario: Mapped["UserScenario"] = relationship(back_populates="parameters")
    records: Mapped[list["Record"]] = relationship(back_populates="parameter")


class Record(BaseModel):
    __tablename__ = "records"
    id: Mapped[int] = mapped_column(primary_key=True)
    parameter_id: Mapped[int] = mapped_column(
        ForeignKey("parameters.id", ondelete="CASCADE"), nullable=False
    )
    value: Mapped[str] = mapped_column(String(150), nullable=False)
    datetime: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    parameter: Mapped["Parameter"] = relationship(back_populates="records")


# pylint: enable={E1136}
