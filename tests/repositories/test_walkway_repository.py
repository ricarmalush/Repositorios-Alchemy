# backend/SQLALCHEMY_REGADIO/tests/repositories/test_walkway_repository.py

import pytest
from sqlalchemy.orm import Session
import datetime

# Importa el modelo Walkway
from database.models.walkway import Walkway
# Importa el repositorio de Walkway
from repositories.walkway_repository import WalkwayRepository

@pytest.fixture
def walkway_repository(db_session: Session) -> WalkwayRepository:
    """Proporciona una instancia de WalkwayRepository para los tests."""
    return WalkwayRepository(db_session)

@pytest.fixture
def new_walkway_data() -> dict:
    """Proporciona datos válidos para crear un nuevo Walkway."""
    return {
        "name": "Jardin Central",
        "location_description": "Zona A, sector 2",
        "is_active": True,
        # created_at se genera automáticamente por el modelo
    }

@pytest.fixture
def existing_walkway(db_session: Session) -> Walkway:
    """Crea y devuelve un Walkway existente en la base de datos."""
    walkway = Walkway(
        name="Paseo del Sol",
        location_description="Al lado del agua",
        is_active=True,
    )
    db_session.add(walkway)
    db_session.commit()
    db_session.refresh(walkway)
    return walkway

def test_create_walkway(walkway_repository: WalkwayRepository, new_walkway_data: dict):
    """Verifica que se puede crear un nuevo andador."""
    created_walkway = walkway_repository.create(new_walkway_data)

    assert created_walkway is not None
    assert created_walkway.id is not None
    assert created_walkway.name == new_walkway_data["name"]
    assert created_walkway.location_description == new_walkway_data["location_description"]
    assert created_walkway.is_active == new_walkway_data["is_active"]
    assert isinstance(created_walkway.created_at, datetime.datetime)

def test_get_walkway_by_id(walkway_repository: WalkwayRepository, existing_walkway: Walkway):
    """Verifica que se puede obtener un andador por su ID."""
    found_walkway = walkway_repository.get_by_id(existing_walkway.id)
    assert found_walkway is not None
    assert found_walkway.id == existing_walkway.id
    assert found_walkway.name == existing_walkway.name

def test_get_walkway_by_id_not_found(walkway_repository: WalkwayRepository):
    """Verifica que se devuelve None si el andador no existe."""
    found_walkway = walkway_repository.get_by_id(9999) # ID que no existe
    assert found_walkway is None

def test_get_by_name(walkway_repository: WalkwayRepository, existing_walkway: Walkway):
    """Verifica que se puede obtener un andador por su nombre."""
    found_walkway = walkway_repository.get_by_name(existing_walkway.name)
    assert found_walkway is not None
    assert found_walkway.id == existing_walkway.id
    assert found_walkway.name == existing_walkway.name

def test_get_by_name_not_found(walkway_repository: WalkwayRepository):
    """Verifica que se devuelve None si el andador por nombre no existe."""
    found_walkway = walkway_repository.get_by_name("NombreInexistente")
    assert found_walkway is None

def test_get_all_walkways(walkway_repository: WalkwayRepository, existing_walkway: Walkway, db_session: Session):
    """Verifica que se pueden obtener todos los andadores."""
    # Crear otro andador para asegurar que hay más de uno
    another_walkway = Walkway(name="Sendero Norte", location_description="Area Verde", is_active=False)
    db_session.add(another_walkway)
    db_session.commit()

    all_walkways = walkway_repository.get_all()
    assert len(all_walkways) >= 2 # Podría haber otros de tests anteriores si no se limpia bien la DB
    assert any(w.name == existing_walkway.name for w in all_walkways)
    assert any(w.name == another_walkway.name for w in all_walkways)

def test_update_walkway(walkway_repository: WalkwayRepository, existing_walkway: Walkway):
    """Verifica que se puede actualizar un andador existente."""
    update_data = {"name": "Paseo del Rio", "location_description=": "Al lado del agua", "is_active": False}
    updated_walkway = walkway_repository.update(existing_walkway.id, update_data)

    assert updated_walkway is not None
    assert updated_walkway.id == existing_walkway.id
    assert updated_walkway.name == "Paseo del Rio"
    assert updated_walkway.location_description == "Al lado del agua"
    assert updated_walkway.is_active == False

    # Verificar que los cambios se persisten en la DB
    retrieved_walkway = walkway_repository.get_by_id(existing_walkway.id)
    assert retrieved_walkway.name == "Paseo del Rio"
    assert retrieved_walkway.location_description == "Al lado del agua"
    assert retrieved_walkway.is_active == False

def test_update_walkway_not_found(walkway_repository: WalkwayRepository):
    """Verifica que update devuelve None si el andador no existe."""
    update_data = {"name": "NoExiste"}
    updated_walkway = walkway_repository.update(9999, update_data)
    assert updated_walkway is None

def test_delete_walkway(walkway_repository: WalkwayRepository, existing_walkway: Walkway):
    """Verifica que se puede eliminar un andador."""
    is_deleted = walkway_repository.delete(existing_walkway.id)
    assert is_deleted is True

    # Verificar que ya no existe
    deleted_walkway = walkway_repository.get_by_id(existing_walkway.id)
    assert deleted_walkway is None

def test_delete_walkway_not_found(walkway_repository: WalkwayRepository):
    """Verifica que delete devuelve False si el andador no existe."""
    is_deleted = walkway_repository.delete(9999)
    assert is_deleted is False