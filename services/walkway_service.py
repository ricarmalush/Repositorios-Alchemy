# services/walkway_service.py

from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.exc import IntegrityError

from repositories.walkway_repository import WalkwayRepository
from database.models.walkway import Walkway
from Core.exceptions import NotFoundError, OperationFailedError, EmptyValueError, IntegrityConstraintError, DuplicateNameError
from Core.error_messages import GeneralErrors

class WalkwayService:
    def __init__(self, db: Session):
        self.walkway_repo = WalkwayRepository(db)
        self.db = db

    def get_walkways(self) -> List[Walkway]:
        """Obtiene todas las pasarelas."""
        return self.walkway_repo.get_all()

    def get_walkway_by_id(self, walkway_id: int) -> Optional[Walkway]:
        """Obtiene una pasarela por su ID."""
        return self.walkway_repo.get_by_id(walkway_id)

    def create_walkway(self, name: str, location_description: str, is_active: bool) -> Walkway:
        """Crea una nueva pasarela con validación."""
        if not name or not name.strip():
            raise EmptyValueError(field_name="nombre")
        
        existing_walkway = self.walkway_repo.get_by_name(name)
        if existing_walkway:
            raise DuplicateNameError(name=name, entity_name="pasarela")

        try:
            return self.walkway_repo.create({
                "name": name,
                "location_description": location_description, 
                "is_active": is_active
            })
        except Exception as e:
            self.db.rollback()
            raise OperationFailedError(
                entity_name="pasarela",
                operation="crear",
                original_exception=e
            )

    def update_walkway(self, walkway_id: int, name: str, location_description: str, is_active: bool) -> Walkway:
        """Actualiza una pasarela existente."""
        if not name or not name.strip():
            raise EmptyValueError(field_name="nombre")
        
        walkway = self.walkway_repo.get_by_id(walkway_id)
        if not walkway:
            raise NotFoundError(entity_name="Pasarela", entity_id=walkway_id)
        
        existing_walkway = self.walkway_repo.get_by_name(name)
        if existing_walkway and existing_walkway.id != walkway_id:
            raise DuplicateNameError(name=name, entity_name="pasarela")

        try:
            return self.walkway_repo.update(walkway_id, {
                "name": name,
                "location_description": location_description, 
                "is_active": is_active
            })
        except IntegrityError as e:
            self.db.rollback()
            raise IntegrityConstraintError(
                f"Ya existe una pasarela con el nombre '{name}'.",
                original_exception=e
            )
        except Exception as e:
            self.db.rollback()
            raise OperationFailedError(
                entity_name="pasarela",
                operation="actualizar",
                original_exception=e
            )

    def delete_walkway(self, walkway_id: int) -> bool:
        """Elimina una pasarela existente."""
        walkway = self.walkway_repo.get_by_id(walkway_id)
        if not walkway:
            raise NotFoundError(entity_name="Pasarela", entity_id=walkway_id)
        
        try:
            return self.walkway_repo.delete(walkway_id)
        except IntegrityError as e:
            self.db.rollback()
            raise IntegrityConstraintError(
                "No se puede eliminar la pasarela porque está en uso.",
                original_exception=e
            )
        except Exception as e:
            self.db.rollback()
            raise OperationFailedError(
                entity_name="pasarela",
                operation="eliminar",
                original_exception=e
            )
