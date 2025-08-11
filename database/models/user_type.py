# database/models/user_type.py (Versión Corregida)

from __future__ import annotations
from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ..base import Base

#  Es una parte clave del módulo typing de Python y se utiliza para evitar problemas de "importación circular" al usar sugerencias de tipos (type hints).
if TYPE_CHECKING:
    from .access_schedule_rule import AccessScheduleRule

class UserType(Base):
    __tablename__ = "user_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Relación uno-a-muchos con AccessScheduleRule
    access_schedule_rules: Mapped[List["AccessScheduleRule"]] = relationship(
        back_populates="user_type",
        cascade="all, delete-orphan"
    )


    def __repr__(self):
        return f"<UserType(id={self.id}, name='{self.name}')>"