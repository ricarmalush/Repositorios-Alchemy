from __future__ import annotations
from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ..base import Base
import datetime

from typing import List
# from ..base import Base # Ya importado arriba

class WateringEvent(Base):
    __tablename__ = 'watering_events'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    start_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    # AÑADIDO: end_time como columna mapeada, ya que se usa en los tests
    end_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    volume_liters: Mapped[float] = mapped_column(Float, nullable=False)

    # Claves Foráneas
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    walkway_id: Mapped[int] = mapped_column(Integer, ForeignKey('walkways.id'))
    schedule_id: Mapped[int] = mapped_column(Integer, ForeignKey('user_watering_schedules.id'), nullable=False)

    # Relaciones
    user: Mapped["User"] = relationship("database.models.user.User", back_populates="watering_events")
    walkway: Mapped["Walkway"] = relationship("database.models.walkway.Walkway", back_populates="watering_events")
    schedule: Mapped["UserWateringSchedule"] = relationship("database.models.user_watering_schedule.UserWateringSchedule", back_populates="watering_events")

    def __repr__(self):
        return f"<WateringEvent(id={self.id}, start_time='{self.start_time}', end_time='{self.end_time}', volume_liters={self.volume_liters})>"

