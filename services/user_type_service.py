# services/user_type_service.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from repositories.user_type_repository import UserTypeRepository
from database.models.user_type import UserType
from Core.exceptions import NotFoundError, IntegrityConstraintError, OperationFailedError, EmptyValueError
from Core.error_messages import UserTypeErrors, GeneralErrors

class UserTypeService:
    def __init__(self, db: Session):
        # La llamada al repositorio se ha corregido para pasar solo la sesión de la base de datos
        self.user_type_repo = UserTypeRepository(db)
        self.db = db

    def get_user_types(self) -> List[UserType]:
        """Obtiene todos los tipos de usuario."""
        return self.user_type_repo.get_all()

    def get_user_type_by_id(self, user_type_id: int) -> Optional[UserType]:
        """Obtiene un tipo de usuario por su ID."""
        return self.user_type_repo.get_by_id(user_type_id)

    def create_user_type(self, name: str) -> UserType:
        """Crea un nuevo tipo de usuario con validación."""
        if not name or not name.strip():
            raise EmptyValueError(field_name="nombre")


        try:
            return self.user_type_repo.create({"name": name})
        except IntegrityError as e:
            self.db.rollback()
            raise IntegrityConstraintError(
                f"Ya existe un tipo de usuario con el nombre '{name}'.",
                original_exception=e
            )
        except Exception as e:
            self.db.rollback()
            raise OperationFailedError(
                entity_name="tipo de usuario",
                operation="crear",
                original_exception=e
            )

    def update_user_type(self, user_type_id: int, name: str) -> UserType:
        """Actualiza un tipo de usuario existente."""
        if not name or not name.strip():
            raise EmptyValueError(field_name="nombre")

        user_type = self.user_type_repo.get_by_id(user_type_id)
        if not user_type:
            raise NotFoundError(entity_name="Tipo de usuario", entity_id=user_type_id)


        try:
            return self.user_type_repo.update(user_type_id, {"name": name})
        except IntegrityError as e:
            self.db.rollback()
            raise IntegrityConstraintError(
                f"Ya existe un tipo de usuario con el nombre '{name}'.",
                original_exception=e
            )
        except Exception as e:
            self.db.rollback()
            raise OperationFailedError(
                entity_name="tipo de usuario",
                operation="actualizar",
                original_exception=e
            )

    def delete_user_type(self, user_type_id: int) -> bool:
        """Elimina un tipo de usuario existente."""
        user_type = self.user_type_repo.get_by_id(user_type_id)
        if not user_type:
            raise NotFoundError(entity_name="Tipo de usuario", entity_id=user_type_id)
        
        try:
            return self.user_type_repo.delete(user_type_id)
        except IntegrityError as e:
            self.db.rollback()
            raise IntegrityConstraintError(
                UserTypeErrors.HAS_ASSOCIATED_USERS.format(user_type_id=user_type_id),
                original_exception=e
            )
        except Exception as e:
            self.db.rollback()
            raise OperationFailedError(
                entity_name="tipo de usuario",
                operation="eliminar",
                original_exception=e
            )

