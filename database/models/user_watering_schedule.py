from __future__ import annotations
from typing import List

from sqlalchemy import Integer, Date, Time, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from ..base import Base
import datetime


class UserWateringSchedule(Base):
    __tablename__ = 'user_watering_schedules'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scheduled_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    start_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    end_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now, nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship("database.models.user.User", back_populates="user_watering_schedules")
    watering_events: Mapped[List["WateringEvent"]] = relationship(back_populates="schedule")

    def __repr__(self):
        return (f"<UserWateringSchedule(id={self.id}, user_id={self.user_id}, "
                f"scheduled_date={self.scheduled_date}, start_time={self.start_time}, "
                f"end_time={self.end_time})>")