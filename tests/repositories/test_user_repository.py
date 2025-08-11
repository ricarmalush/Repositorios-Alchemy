# backend/SQLALCHEMY_REGADIO/tests/repositories/test_user_repository.py

import pytest
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import time

from repositories.user_repository import UserRepository
from database.models.user import User
from database.models.walkway import Walkway
from database.models.user_type import UserType
from database.models.access_schedule_rule import AccessScheduleRule

# Nota: El fixture 'db_session' se asume que está provisto por conftest.py
# y proporciona una sesión de base de datos transaccional para cada test.

@pytest.fixture
def user_repo(db_session: Session) -> UserRepository:
    """Fixture que proporciona una instancia del UserRepository."""
    return UserRepository(db_session)

@pytest.fixture
def prerequisite_data(db_session: Session):
    """
    Fixture que crea y devuelve los datos prerequisitos para los tests de User,
    incluyendo las llaves foráneas.
    """
    # Crear una instancia de Walkway con todos los campos obligatorios
    walkway = Walkway(name="Test Walkway", location_description="A test location")
    db_session.add(walkway)
    db_session.commit()

    # Crear una instancia de UserType
    user_type = UserType(name="Test Type")
    db_session.add(user_type)
    db_session.commit()

    # Crear una instancia de AccessScheduleRule con todos los campos obligatorios.
    # Usamos los IDs de los objetos Walkway y UserType que acabamos de crear.
    access_rule = AccessScheduleRule(
        rule_name="Test Access Rule",
        day_of_week="Monday",
        start_time=time(8, 0, 0),
        end_time=time(17, 0, 0),
        user_type=user_type,
        walkway=walkway
    )
    db_session.add(access_rule)
    db_session.commit()

    return {
        "walkway_id": walkway.id,
        "user_type_id": user_type.id,
        "access_schedule_rule_id": access_rule.id
    }

def test_create_user(user_repo: UserRepository, db_session: Session, prerequisite_data):
    """Verifica la creación exitosa de un usuario con todas las llaves foráneas."""
    # Arrange
    user_data = {
        "name":"newname",
        "username": "newuser",
        "email": "newuser@example.com",
        "password_hash": "hashed_password",
        "first_name": "New",
        "last_name": "User",
        "phone_number": "123456789",
        "walkway_id": prerequisite_data["walkway_id"],
        "user_type_id": prerequisite_data["user_type_id"],
        "access_schedule_rule_id": prerequisite_data["access_schedule_rule_id"]
    }

    # Act
    new_user = user_repo.create(user_data)
    
    # Assert
    assert new_user is not None
    assert isinstance(new_user, User)
    assert new_user.name == "newname"
    assert new_user.username == "newuser"
    assert new_user.email == "newuser@example.com"
    assert new_user.walkway_id == prerequisite_data["walkway_id"]
    assert new_user.user_type_id == prerequisite_data["user_type_id"]
    assert new_user.access_schedule_rule_id == prerequisite_data["access_schedule_rule_id"]
    
    # Verifica que el usuario realmente existe en la base de datos
    retrieved_user = db_session.execute(select(User).filter_by(id=new_user.id)).scalar_one_or_none()
    assert retrieved_user is not None
    assert retrieved_user.username == "newuser"

def test_get_by_id(user_repo: UserRepository, prerequisite_data):
    """Verifica la obtención de un usuario por su ID."""
    # Arrange
    user = user_repo.create({
        "name": "newname",
        "username": "user1",
        "email": "user1@example.com",
        "password_hash": "hashed_password",
        "first_name": "User",
        "last_name": "One",
        "phone_number": "123456789",
        "walkway_id": prerequisite_data["walkway_id"],
        "user_type_id": prerequisite_data["user_type_id"],
        "access_schedule_rule_id": prerequisite_data["access_schedule_rule_id"]
    })

    # Act
    retrieved_user = user_repo.get_by_id(user.id)

    # Assert
    assert retrieved_user is not None
    assert retrieved_user.username == "user1"

def test_get_by_id_not_found(user_repo: UserRepository):
    """Verifica que devuelve None si el usuario no existe."""
    # Act
    retrieved_user = user_repo.get_by_id(999) # ID que no existe

    # Assert
    assert retrieved_user is None

def test_get_by_username(user_repo: UserRepository, prerequisite_data):
    """Verifica la obtención de un usuario por su nombre de usuario."""
    # Arrange
    user = user_repo.create({
        "name": "newname",
        "username": "user_test",
        "email": "user_test@example.com",
        "password_hash": "hashed_password",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "123456789",
        "walkway_id": prerequisite_data["walkway_id"],
        "user_type_id": prerequisite_data["user_type_id"],
        "access_schedule_rule_id": prerequisite_data["access_schedule_rule_id"]
    })

    # Act
    retrieved_user = user_repo.get_by_username("user_test")

    # Assert
    assert retrieved_user is not None
    assert retrieved_user.username == "user_test"

def test_get_by_username_not_found(user_repo: UserRepository):
    """Verifica que devuelve None si el nombre de usuario no existe."""
    # Act
    retrieved_user = user_repo.get_by_username("non_existent_user")

    # Assert
    assert retrieved_user is None

def test_get_by_email(user_repo: UserRepository, prerequisite_data):
    """Verifica la obtención de un usuario por su email."""
    # Arrange
    user = user_repo.create({
        "name": "newname",
        "username": "email_user",
        "email": "email_user@example.com",
        "password_hash": "hashed_password",
        "first_name": "Email",
        "last_name": "User",
        "phone_number": "123456789",
        "walkway_id": prerequisite_data["walkway_id"],
        "user_type_id": prerequisite_data["user_type_id"],
        "access_schedule_rule_id": prerequisite_data["access_schedule_rule_id"]
    })

    # Act
    retrieved_user = user_repo.get_by_email("email_user@example.com")

    # Assert
    assert retrieved_user is not None
    assert retrieved_user.email == "email_user@example.com"

def test_get_by_email_not_found(user_repo: UserRepository):
    """Verifica que devuelve None si el email no existe."""
    # Act
    retrieved_user = user_repo.get_by_email("non_existent@example.com")

    # Assert
    assert retrieved_user is None

def test_update_user(user_repo: UserRepository, db_session: Session, prerequisite_data):
    """Verifica la actualización de un usuario."""
    # Arrange
    user = user_repo.create({
        "name": "newname",
        "username": "to_update",
        "email": "to_update@example.com",
        "password_hash": "hashed_password",
        "first_name": "To",
        "last_name": "Update",
        "phone_number": "123456789",
        "walkway_id": prerequisite_data["walkway_id"],
        "user_type_id": prerequisite_data["user_type_id"],
        "access_schedule_rule_id": prerequisite_data["access_schedule_rule_id"]
    })
    update_data = {"email": "updated@example.com"}

    # Act
    updated_user = user_repo.update(user.id, update_data)

    # Assert
    assert updated_user is not None
    assert updated_user.email == "updated@example.com"
    
    retrieved_user = db_session.execute(select(User).filter_by(id=user.id)).scalar_one_or_none()
    assert retrieved_user.email == "updated@example.com"

def test_delete_user(user_repo: UserRepository, db_session: Session, prerequisite_data):
    """Verifica la eliminación de un usuario."""
    # Arrange
    user = user_repo.create({
        "name": "newname",
        "username": "to_delete",
        "email": "to_delete@example.com",
        "password_hash": "hashed_password",
        "first_name": "To",
        "last_name": "Delete",
        "phone_number": "123456789",
        "walkway_id": prerequisite_data["walkway_id"],
        "user_type_id": prerequisite_data["user_type_id"],
        "access_schedule_rule_id": prerequisite_data["access_schedule_rule_id"]
    })
    user_id = user.id

    # Act
    is_deleted = user_repo.delete(user_id)

    # Assert
    assert is_deleted is True
    retrieved_user = db_session.execute(select(User).filter_by(id=user_id)).scalar_one_or_none()
    assert retrieved_user is None