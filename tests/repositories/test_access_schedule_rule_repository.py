# backend/SQLALCHEMY_REGADIO/tests/repositories/test_access_schedule_rule_repository.py
from datetime import time
import pytest
from sqlalchemy.orm import Session
from services.access_schedule_rule_service import AccessScheduleRuleService
from services.user_type_service import UserTypeService
from services.walkway_service import WalkwayService
from database.models.access_schedule_rule import AccessScheduleRule
from Core.exceptions import ValidationError, NotFoundError


def test_service_create_access_rule_success(access_rule_service: AccessScheduleRuleService, user_type_service: UserTypeService, walkway_service: WalkwayService, db_session: Session):
    """Verifica la creación exitosa de una regla a través del servicio."""
    # Arrange
    user_type = user_type_service.create_user_type("Admin")
    walkway = walkway_service.create_walkway("Walkway A", "Description for Walkway A", True)
    
    # Usa flush() para asegurar que el user_type y walkway se guarden en la base de datos y tengan un ID
    # sin hacer un commit permanente.
    db_session.flush()
    
    rule_data = {
        "user_type_id": user_type.id,
        "walkway_id": walkway.id,
        "rule_name": "Test Rule",
        "day_of_week": 0,
        "start_time": "09:00",
        "end_time": "17:00"
    }
    
    # Act
    new_rule = access_rule_service.create_access_rule(rule_data)
    
    # Assert
    assert new_rule is not None
    assert new_rule.id is not None
    assert new_rule.user_type_id == user_type.id
    assert new_rule.walkway_id == walkway.id
    assert new_rule.rule_name == "Test Rule"
    
    # CORRECCIÓN: Se vuelve a convertir a entero para la aserción,
    # ya que el servicio devuelve el valor como string.
    assert int(new_rule.day_of_week) == 0
    
    assert new_rule.start_time == time(9, 0)
    assert new_rule.end_time == time(17, 0)

def test_service_create_access_rule_user_type_not_found(access_rule_service: AccessScheduleRuleService, walkway_service: WalkwayService, db_session: Session):
    """Verifica el manejo de error cuando no se encuentra el user_type."""
    # Arrange
    walkway = walkway_service.create_walkway("Walkway B", "Description for Walkway B", True)
    db_session.flush()
    
    rule_data = {
        "user_type_id": 999, # ID de user_type inexistente
        "walkway_id": walkway.id,
        "rule_name": "Test Rule",
        "day_of_week": 1,
        "start_time": "10:00",
        "end_time": "18:00"
    }
    
    # Act & Assert
    with pytest.raises(NotFoundError, match="El tipo de usuario con ID 999 no existe."):
        access_rule_service.create_access_rule(rule_data)

def test_service_create_access_rule_invalid_day_of_week(access_rule_service: AccessScheduleRuleService, user_type_service: UserTypeService, walkway_service: WalkwayService, db_session: Session):
    """Verifica el manejo de error para un día de la semana inválido."""
    # Arrange
    user_type = user_type_service.create_user_type("Admin")
    walkway = walkway_service.create_walkway("Walkway C", "Description for Walkway C", True)
    db_session.flush()

    rule_data = {
        "user_type_id": user_type.id,
        "walkway_id": walkway.id,
        "rule_name": "Test Rule",
        "day_of_week": 7, # Día de la semana inválido (debe ser 0-6)
        "start_time": "11:00",
        "end_time": "19:00"
    }
    
    # Act & Assert
    with pytest.raises(ValidationError, match="El día de la semana no es válido. Debe ser un número entre 0 \\(lunes\\) y 6 \\(domingo\\)."):
        access_rule_service.create_access_rule(rule_data)

def test_service_create_access_rule_invalid_time_range(access_rule_service: AccessScheduleRuleService, user_type_service: UserTypeService, walkway_service: WalkwayService, db_session: Session):
    """Verifica el manejo de error para un rango de tiempo inválido."""
    # Arrange
    user_type = user_type_service.create_user_type("Admin")
    walkway = walkway_service.create_walkway("Walkway D", "Description for Walkway D", True)
    db_session.flush()

    rule_data = {
        "user_type_id": user_type.id,
        "walkway_id": walkway.id,
        "rule_name": "Test Rule",
        "day_of_week": 2,
        "start_time": "19:00",
        "end_time": "11:00" # Rango de tiempo inválido (start > end)
    }
    
    # Act & Assert
    with pytest.raises(ValidationError, match="La hora de inicio \\(.*\\) no puede ser posterior o igual a la hora de fin \\(.*\\)."):
        access_rule_service.create_access_rule(rule_data)

def test_service_delete_access_rule_not_found(access_rule_service: AccessScheduleRuleService):
    """Verifica el manejo de error cuando no se encuentra la regla a eliminar."""
    # Act & Assert
    with pytest.raises(NotFoundError, match="Regla de acceso con ID 999 no encontrada."):
        access_rule_service.delete_access_rule(999)
