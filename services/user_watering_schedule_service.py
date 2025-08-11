# services/user_watering_schedule_service.py

from sqlalchemy.orm import Session
from typing import Optional, List
import datetime

from Core.error_messages import (
    UserErrors,
    AccessScheduleRuleErrors,
    UserWateringScheduleErrors,
    GeneralErrors
)

from repositories.user_watering_schedule_repository import UserWateringScheduleRepository
from repositories.user_repository import UserRepository
from repositories.access_schedule_rule_repository import AccessScheduleRuleRepository
from repositories.walkway_repository import WalkwayRepository


class UserWateringScheduleService:
    def __init__(self, db: Session):
        self.user_watering_schedule_repo = UserWateringScheduleRepository(db)
        self.user_repo = UserRepository(db)
        self.access_rule_repo = AccessScheduleRuleRepository(db)
        self.walkway_repo = WalkwayRepository(db)
        self.db = db

    def create_schedule(self, schedule_data: dict) -> Optional[UserWateringScheduleRepository.model]:
        user_id = schedule_data['user_id']
        access_rule_id = schedule_data['access_schedule_rule_id']
        start_time = schedule_data['start_time']
        end_time = schedule_data['end_time']

        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(UserErrors.NOT_FOUND.format(user_id=user_id))

        access_rule = self.access_rule_repo.get_by_id(access_rule_id)
        if not access_rule:
            raise ValueError(AccessScheduleRuleErrors.RULE_NOT_FOUND.format(rule_id=access_rule_id))

        if start_time >= end_time:
            raise ValueError(AccessScheduleRuleErrors.INVALID_TIME_RANGE.format(start_time=start_time.time(), end_time=end_time.time()))

        max_duration_minutes = 120
        if (end_time - start_time).total_seconds() / 60 > max_duration_minutes:
            raise ValueError(UserWateringScheduleErrors.MAX_DURATION_EXCEEDED.format(max_duration_minutes=max_duration_minutes))

        overlapping_schedules = self.user_watering_schedule_repo.get_overlapping_schedules(
            user_id=user_id,
            start_time=start_time,
            end_time=end_time
        )
        if overlapping_schedules:
            raise ValueError(UserWateringScheduleErrors.OVERLAPPING_SCHEDULE)
        
        proposed_day_of_week = start_time.weekday()

        user_type_access_rules = self.access_rule_repo.get_by_user_type_and_day(
            user_type_id=user.user_type_id,
            day_of_week=proposed_day_of_week
        )

        is_allowed = False
        for rule in user_type_access_rules:
            proposed_start_time_only = start_time.time()
            proposed_end_time_only = end_time.time()

            if rule.start_time <= proposed_start_time_only and rule.end_time >= proposed_end_time_only:
                is_allowed = True
                break
        
        if not is_allowed:
            raise ValueError(UserWateringScheduleErrors.SCHEDULE_RULE_MISMATCH)

        try:
            new_schedule = self.user_watering_schedule_repo.create(schedule_data)
            return new_schedule
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(GeneralErrors.UNEXPECTED_ERROR.format(operation="crear", entity_name="programación de riego", detail=str(e)))

    def get_schedule_by_id(self, schedule_id: int) -> Optional[UserWateringScheduleRepository.model]:
        return self.user_watering_schedule_repo.get_by_id(schedule_id)

    def get_schedules_for_user(self, user_id: int, date: Optional[datetime.date] = None) -> List[UserWateringScheduleRepository.model]:
        return self.user_watering_schedule_repo.get_schedules_for_user(user_id, date)

    def update_schedule(self, schedule_id: int, update_data: dict) -> Optional[UserWateringScheduleRepository.model]:
        schedule = self.user_watering_schedule_repo.get_by_id(schedule_id)
        if not schedule:
            raise ValueError(UserWateringScheduleErrors.NOT_FOUND.format(schedule_id=schedule_id))

        if 'start_time' in update_data and 'end_time' in update_data:
            if update_data['start_time'] >= update_data['end_time']:
                raise ValueError(AccessScheduleRuleErrors.INVALID_TIME_RANGE.format(start_time=update_data['start_time'].time(), end_time=update_data['end_time'].time()))

            user = self.user_repo.get_by_id(schedule.user_id)
            
            overlapping_schedules = self.user_watering_schedule_repo.get_overlapping_schedules(
                user_id=schedule.user_id,
                start_time=update_data['start_time'],
                end_time=update_data['end_time'],
                exclude_schedule_id=schedule_id
            )
            if overlapping_schedules:
                raise ValueError(UserWateringScheduleErrors.UPDATE_OVERLAPPING_SCHEDULE)

            if 'access_schedule_rule_id' in update_data:
                 new_access_rule_id = update_data['access_schedule_rule_id']
            else:
                 new_access_rule_id = schedule.access_schedule_rule_id
                 
            access_rule = self.access_rule_repo.get_by_id(new_access_rule_id)
            if not access_rule:
                raise ValueError(AccessScheduleRuleErrors.RULE_NOT_FOUND.format(rule_id=new_access_rule_id))

            proposed_day_of_week = update_data['start_time'].weekday()
            user_type_access_rules = self.access_rule_repo.get_by_user_type_and_day(
                user_type_id=user.user_type_id,
                day_of_week=proposed_day_of_week
            )
            is_allowed = False
            for rule in user_type_access_rules:
                proposed_start_time_only = update_data['start_time'].time()
                proposed_end_time_only = update_data['end_time'].time()
                if rule.start_time <= proposed_start_time_only and rule.end_time >= proposed_end_time_only:
                    is_allowed = True
                    break
            if not is_allowed:
                raise ValueError(UserWateringScheduleErrors.UPDATE_SCHEDULE_RULE_MISMATCH)

        for key in ['id', 'user_id', 'created_at']:
            update_data.pop(key, None)

        if not update_data:
            return schedule

        try:
            updated_schedule = self.user_watering_schedule_repo.update(schedule_id, update_data)
            return updated_schedule
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(GeneralErrors.UNEXPECTED_ERROR.format(operation="actualizar", entity_name="programación de riego", detail=str(e)))

    def delete_schedule(self, schedule_id: int) -> bool:
        try:
            return self.user_watering_schedule_repo.delete(schedule_id)
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(GeneralErrors.UNEXPECTED_ERROR.format(operation="eliminar", entity_name="programación de riego", detail=str(e)))

    def get_all_schedules(self, skip: int = 0, limit: int = 100) -> List[UserWateringScheduleRepository.model]:
        return self.user_watering_schedule_repo.get_all(skip=skip, limit=limit)

    def get_schedules_for_walkway_on_date(self, walkway_id: int, date: datetime.date) -> List[UserWateringScheduleRepository.model]:
        return self.user_watering_schedule_repo.get_schedules_for_walkway_on_date(walkway_id, date)