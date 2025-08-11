# backend/SQLALCHEMY_REGADIO/database/models/user.py

from __future__ import annotations
from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from ..base import Base
import datetime

from typing import List
from .user_type import UserType
from .walkway import Walkway
from .access_schedule_rule import AccessScheduleRule
from .user_watering_schedule import UserWateringSchedule
from .watering_event import WateringEvent
from .notification import Notification


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now, nullable=False)
    last_login: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)

    # Claves Foráneas
    user_type_id: Mapped[int] = mapped_column(Integer, ForeignKey('user_types.id'), nullable=False)
    walkway_id: Mapped[int] = mapped_column(Integer, ForeignKey('walkways.id'), nullable=False)
    access_schedule_rule_id: Mapped[int] = mapped_column(Integer, ForeignKey('access_schedule_rules.id'),nullable=False)

    # La relación con user_type es UNIDIRECCIONAL, ya que user_type no depende de User.
    user_type: Mapped["UserType"] = relationship("database.models.user_type.UserType")

    # La relación con walkway es bidireccional, asumimos que walkway tiene una lista de usuarios.
    walkway: Mapped["Walkway"] = relationship("database.models.walkway.Walkway", back_populates="users")

    # La relación con access_schedule_rule también es UNIDIRECCIONAL.
    # El usuario depende de la regla, pero la regla no depende del usuario.
    access_schedule_rule: Mapped["AccessScheduleRule"] = relationship("database.models.access_schedule_rule.AccessScheduleRule")
    # -------------------------------------------------------------

    # Las siguientes relaciones son bidireccionales y permiten un acceso fácil. Esto es lo mismo que las propiedades de navegación en .net
    # desde un objeto de usuario a sus programaciones, eventos y notificaciones.
    user_watering_schedules: Mapped[List["UserWateringSchedule"]] = relationship("database.models.user_watering_schedule.UserWateringSchedule", back_populates="user")
    watering_events: Mapped[List["WateringEvent"]] = relationship("database.models.watering_event.WateringEvent", back_populates="user")
    notifications: Mapped[List["Notification"]] = relationship("database.models.notification.Notification", back_populates="user")

    def __repr__(self):
        return (f"<User(id={self.id}, username='{self.username}', "
                f"email='{self.email}', user_type_id={self.user_type_id})>")