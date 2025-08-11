# repositories/watering_event_repository.py

import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List

# Importamos el modelo WateringEvent
from database.models.watering_event import WateringEvent
from database.models.user import User # Posiblemente para filtrar por usuario

# Importamos nuestro BaseRepository genérico
from .base_repository import BaseRepository


class WateringEventRepository(BaseRepository[WateringEvent]):
    """
    Repositorio específico para el modelo WateringEvent, heredando las operaciones CRUD básicas
    y añadiendo métodos específicos para la gestión de eventos de riego.
    """
    def __init__(self, db: Session):
        super().__init__(db, WateringEvent)

    def get_events_for_user(self, user_id: int, start_date: datetime.date | None = None, end_date: datetime.date | None = None) -> List[WateringEvent]:
        """
        Obtiene los eventos de riego para un usuario específico, opcionalmente filtrados por un rango de fechas.
        """
        query = select(WateringEvent).join(User).filter(User.id == user_id)
        
        if start_date:
            query = query.filter(WateringEvent.start_time >= start_date)
        if end_date:
            # Asegura que el final del día de end_date se incluya
            query = query.filter(WateringEvent.start_time <= (end_date + datetime.timedelta(days=1)))
            
        return self.db.execute(query.order_by(WateringEvent.start_time.desc())).scalars().all()

    def get_events_by_schedule(self, schedule_id: int) -> List[WateringEvent]:
        """
        Obtiene todos los eventos de riego asociados a una programación de riego específica.
        """
        return self.db.execute(
            select(WateringEvent).filter_by(schedule_id=schedule_id)
            .order_by(WateringEvent.start_time.desc())
        ).scalars().all()

    def get_recent_events(self, limit: int = 10) -> List[WateringEvent]:
        """
        Obtiene los eventos de riego más recientes.
        """
        return self.db.execute(
            select(WateringEvent)
            .order_by(WateringEvent.start_time.desc())
            .limit(limit)
        ).scalars().all()

    def get_total_water_used(self, start_date: datetime.date | None = None, end_date: datetime.date = None) -> float:
        """
        Calcula el volumen total de agua utilizada en un rango de fechas.
        Asume que WateringEvent tiene un campo 'volume_liters' o similar.
        """
        query = select(func.sum(WateringEvent.volume_liters)) 
        
        if start_date:
            query = query.filter(WateringEvent.start_time >= start_date)
        if end_date:
            query = query.filter(WateringEvent.start_time <= (end_date + datetime.timedelta(days=1)))
            
        total_volume = self.db.execute(query).scalar_one_or_none()
        return float(total_volume) if total_volume is not None else 0.0