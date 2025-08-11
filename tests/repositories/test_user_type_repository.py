# tests/repositories/test_user_type_repository.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from repositories.user_type_repository import UserTypeRepository
from database.models.user_type import UserType
import datetime

def test_create_user_type(db_session: Session):
    """
    Test para verificar que se puede crear un tipo de usuario.
    """
    # 1. Arrange (Preparar)
    user_type_repo = UserTypeRepository(db=db_session)
    user_type_data = {"name": "Administrador"}
    
    # 2. Act (Actuar)
    new_user_type = user_type_repo.create(user_type_data)
    
    # 3. Assert (Verificar)
    assert new_user_type is not None
    assert new_user_type.name == "Administrador"
    assert db_session.get(UserType, new_user_type.id) is not None

def test_get_user_type_by_id(db_session: Session):
    """
    Test para verificar que se puede obtener un tipo de usuario por su ID.
    """
    # 1. Arrange (Preparar)
    user_type_repo = UserTypeRepository(db=db_session)
    existing_user_type = user_type_repo.create({"name": "Cliente"})
    
    # 2. Act (Actuar)
    found_user_type = user_type_repo.get_by_id(existing_user_type.id)

    # 3. Assert (Verificar)
    assert found_user_type is not None
    assert found_user_type.id == existing_user_type.id
    assert found_user_type.name == "Cliente"

def test_get_user_type_by_name(db_session: Session):
    """
    Test para verificar que se puede obtener un tipo de usuario por su nombre.
    """
    # 1. Arrange (Preparar)
    user_type_repo = UserTypeRepository(db=db_session)
    existing_type_data = {"name": "Editor"}
    user_type_repo.create(existing_type_data)
    
    # 2. Act (Actuar)
    found_user_type = user_type_repo.get_by_name(existing_type_data["name"])

    # 3. Assert (Verificar)
    assert found_user_type is not None
    assert found_user_type.name == "Editor"

def test_get_all_user_types(db_session: Session):
    """
    Test para verificar que se pueden obtener todos los tipos de usuario.
    """
    # 1. Arrange (Preparar)
    user_type_repo = UserTypeRepository(db=db_session)
    # Crear varios tipos de usuario
    user_type_repo.create({"name": "Admin"})
    user_type_repo.create({"name": "Guest"})
    user_type_repo.create({"name": "Subscriber"})
    
    # 2. Act (Actuar)
    all_user_types = user_type_repo.get_all()
    
    # 3. Assert (Verificar)
    assert len(all_user_types) == 3

def test_update_user_type(db_session: Session):
    """
    Test para verificar que se puede actualizar un tipo de usuario.
    """
    # 1. Arrange (Preparar)
    user_type_repo = UserTypeRepository(db=db_session)
    existing_user_type = user_type_repo.create({"name": "Moderador"})
    
    # 2. Act (Actuar)
    update_data = {"name": "Supervisor"}
    updated_user_type = user_type_repo.update(existing_user_type.id, update_data)
    
    # 3. Assert (Verificar)
    assert updated_user_type is not None
    assert updated_user_type.name == "Supervisor"
    # Comprobar que el cambio se ha guardado
    db_session.refresh(updated_user_type)
    assert db_session.get(UserType, updated_user_type.id).name == "Supervisor"

def test_delete_user_type(db_session: Session):
    """
    Test para verificar que se puede eliminar un tipo de usuario.
    """
    # 1. Arrange (Preparar)
    user_type_repo = UserTypeRepository(db=db_session)
    user_type_to_delete = user_type_repo.create({"name": "Invitado"})
    
    # 2. Act (Actuar)
    delete_result = user_type_repo.delete(user_type_to_delete.id)
    
    # 3. Assert (Verificar)
    assert delete_result is True
    # Comprobar que el usuario ya no existe en la base de datos
    assert user_type_repo.get_by_id(user_type_to_delete.id) is None