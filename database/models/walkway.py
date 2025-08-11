# database/models/walkway.py

from __future__ import annotations
import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ..base import Base

if TYPE_CHECKING:
    # Estos imports son para las anotaciones de tipo
    from .user import User
    from .access_schedule_rule import AccessScheduleRule
    from .watering_event import WateringEvent

class Walkway(Base):
    __tablename__ = 'walkways'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location_description: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now, nullable=False)

    # Relaciones
    users: Mapped[List["User"]] = relationship(
        "database.models.user.User", 
        back_populates="walkway"
    )
    
    # Esta relación ahora tiene la clave foránea correspondiente
    access_schedule_rules: Mapped[List["AccessScheduleRule"]] = relationship(
        "database.models.access_schedule_rule.AccessScheduleRule", 
        back_populates="walkway"
    )

    watering_events: Mapped[List["WateringEvent"]] = relationship(
        "database.models.watering_event.WateringEvent", 
        back_populates="walkway"
    )
    
    def __repr__(self):
        return f"<Walkway(id={self.id}, name='{self.name}', location='{self.location_description}')>"