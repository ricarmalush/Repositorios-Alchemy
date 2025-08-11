# from shared.exceptions import IntegrityConstraintError # Línea original con error
from Core.exceptions import IntegrityConstraintError, NotFoundError, OperationFailedError
from Core.error_messages import AccessScheduleRuleErrors
from repositories.base_repository import BaseRepository
from database.models.access_schedule_rule import AccessScheduleRule
from sqlalchemy.orm import Session
from typing import List, Optional

class AccessScheduleRuleRepository(BaseRepository[AccessScheduleRule]):
    """
    Repositorio para la entidad AccessScheduleRule, hereda de BaseRepository.
    """
    def __init__(self, db: Session):
        super().__init__(db, AccessScheduleRule)

    # Aquí se puede añadir métodos específicos para la entidad AccessScheduleRule
    # Por ejemplo, un método para buscar reglas por tipo de usuario o por día de la semana.
    def get_rules_by_user_type_and_day(self, user_type_id: int, day_of_week: int) -> List[AccessScheduleRule]:
        """
        Obtiene las reglas de acceso para un tipo de usuario y día de la semana específicos.
        """
        # Tu lógica de consulta iría aquí
        return []

    def get_by_id_and_user_type(self, rule_id: int, user_type_id: int) -> Optional[AccessScheduleRule]:
        """
        Obtiene una regla por su ID, asegurando que pertenece a un tipo de usuario específico.
        """
        # Tu lógica de consulta iría aquí
        return None
