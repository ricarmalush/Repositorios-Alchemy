# database/models/access_schedule_rule.py

from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base
from sqlalchemy import Integer, String, Time, ForeignKey

# Importar el modelo Walkway para la relación
from database.models.walkway import Walkway

if TYPE_CHECKING:
    from .user_type import UserType
    from .walkway import Walkway

class AccessScheduleRule(Base):
    __tablename__ = "access_schedule_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_name = mapped_column(String, index=True, nullable=False)
    day_of_week: Mapped[str] = mapped_column(String(9), nullable=False)
    start_time: Mapped[Time] = mapped_column(Time, nullable=False)
    end_time: Mapped[Time] = mapped_column(Time, nullable=False)
    user_type_id: Mapped[int] = mapped_column(ForeignKey("user_types.id"), nullable=False)
    walkway_id: Mapped[int] = mapped_column(ForeignKey("walkways.id"), nullable=False)

    user_type: Mapped["UserType"] = relationship(
        back_populates="access_schedule_rules"
    )

    # Añadimos la relación que el modelo Walkway espera
    walkway: Mapped["Walkway"] = relationship(
        back_populates="access_schedule_rules"
    )
