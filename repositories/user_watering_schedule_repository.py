# repositories/user_watering_schedule_repository.py

from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List
import datetime

from database.models.user_watering_schedule import UserWateringSchedule
from database.models.user import User
from .base_repository import BaseRepository


class UserWateringScheduleRepository(BaseRepository[UserWateringSchedule]):

    def __init__(self, db: Session):
        super().__init__(db, UserWateringSchedule)

    def get_schedules_for_user(self, user_id: int, date: datetime.date | None) -> List[UserWateringSchedule]:
        """
        Obtiene las programaciones de riego para un usuario específico.
        Puede filtrar opcionalmente por una fecha específica.
        """
        query = select(UserWateringSchedule).filter_by(user_id=user_id)
        if date:
            query = query.filter(UserWateringSchedule.scheduled_date == date)
        
        return self.db.execute(query.order_by(UserWateringSchedule.start_time)).scalars().all()

    def get_overlapping_schedules(self, user_id: int, start_time: datetime.datetime, end_time: datetime.datetime, exclude_schedule_id: int | None = None) -> List[UserWateringSchedule]:
        """
        Obtiene programaciones que se superponen con un rango de tiempo dado para un usuario.
        """
        query = select(UserWateringSchedule).filter(
            UserWateringSchedule.user_id == user_id,
            UserWateringSchedule.scheduled_date == start_time.date(), 
            func.time(UserWateringSchedule.start_time) < end_time.time(), 
            func.time(UserWateringSchedule.end_time) > start_time.time() 
        )

        if exclude_schedule_id:
            query = query.filter(UserWateringSchedule.id != exclude_schedule_id)
            
        return self.db.execute(query).scalars().all()

    def get_upcoming_schedules(self, limit: int = 10) -> List[UserWateringSchedule]:
        """
        Obtiene las próximas programaciones de riego que aún no han comenzado.
        """
        now = datetime.datetime.now()

        return self.db.execute(
            select(UserWateringSchedule)
            .filter(
                func.datetime(UserWateringSchedule.scheduled_date, UserWateringSchedule.start_time) > now
            )
            .order_by(UserWateringSchedule.scheduled_date, UserWateringSchedule.start_time)
            .limit(limit)
        ).scalars().all()

    def get_schedules_for_walkway_on_date(self, walkway_id: int, date: datetime.date) -> List[UserWateringSchedule]:
        """
        Obtiene todas las programaciones de riego para un andador específico en una fecha dada.
        """
        return self.db.execute(
            select(UserWateringSchedule)
            .join(User)
            .filter(
                User.walkway_id == walkway_id,
                UserWateringSchedule.scheduled_date == date
            )
            .order_by(UserWateringSchedule.start_time)
        ).scalars().all()