# services/access_schedule_rule_service.py

from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import time, datetime
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from repositories.access_schedule_rule_repository import AccessScheduleRuleRepository
from repositories.user_type_repository import UserTypeRepository
from database.models.access_schedule_rule import AccessScheduleRule

from Core.exceptions import (
    NotFoundError,
    ValidationError,
    OperationFailedError,
    IntegrityConstraintError,
    ApplicationError
)
from Core.error_messages import AccessScheduleRuleErrors, GeneralErrors

class AccessScheduleRuleService:
    def __init__(self, db: Session):
        self.access_rule_repo = AccessScheduleRuleRepository(db)
        self.user_type_repo = UserTypeRepository(db)
        self.db = db

    def create_access_rule(self, rule_data: Dict[str, Any]) -> AccessScheduleRule:
        """
        Crea una nueva regla de acceso, validando los datos de entrada.
        """
        user_type_id = rule_data.get('user_type_id')
        if not self.user_type_repo.get_by_id(user_type_id):
            raise NotFoundError(
                entity_name="Tipo de usuario",
                entity_id=user_type_id,
                message=AccessScheduleRuleErrors.USER_TYPE_NOT_FOUND.format(user_type_id=user_type_id)
            )

        day_of_week = rule_data.get('day_of_week')
        if not (0 <= day_of_week <= 6):
            raise ValidationError(AccessScheduleRuleErrors.INVALID_DAY_OF_WEEK)

        start_time_str = rule_data.get('start_time')
        end_time_str = rule_data.get('end_time')

        # Convertir strings a objetos datetime.time
        try:
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
        except ValueError:
            raise ValidationError("Formato de hora inválido. Se espera 'HH:MM'.")

        if start_time >= end_time:
            raise ValidationError(AccessScheduleRuleErrors.INVALID_TIME_RANGE)

        rule_data['start_time'] = start_time
        rule_data['end_time'] = end_time

        try:
            return self.access_rule_repo.create(rule_data)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise OperationFailedError(
                entity_name="regla de acceso",
                operation="crear",
                original_exception=e
            )

    def delete_access_rule(self, rule_id: int) -> bool:
        """
        Elimina una regla de acceso existente.
        """
        rule = self.access_rule_repo.get_by_id(rule_id)
        if not rule:
            # Aquí es donde se ha corregido el error
            raise NotFoundError(
                entity_name="Regla de acceso",
                entity_id=rule_id,
                message=AccessScheduleRuleErrors.RULE_NOT_FOUND.format(rule_id=rule_id)
            )
        
        try:
            is_deleted = self.access_rule_repo.delete(rule_id)
            if not is_deleted:
                raise OperationFailedError(entity_name="regla de acceso", operation="eliminar")
            return is_deleted
        except IntegrityError as e:
            self.db.rollback()
            raise IntegrityConstraintError("No se puede eliminar la regla de acceso porque está en uso.", original_exception=e)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise OperationFailedError(
                entity_name="regla de acceso",
                operation="eliminar",
                original_exception=e
            )
