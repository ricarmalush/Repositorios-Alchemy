from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from repositories.base_repository import BaseRepository
from database.models.walkway import Walkway
from Core.exceptions import NotFoundError, IntegrityConstraintError, OperationFailedError

class WalkwayRepository(BaseRepository[Walkway]):
    """
    Repositorio para la entidad Walkway.
    """
    def __init__(self, db: Session):
        super().__init__(db, Walkway)

    def get_by_name(self, name: str) -> Optional[Walkway]:
        """
        Obtiene una pasarela por su nombre.

        Args:
            name (str): El nombre de la pasarela.

        Returns:
            Optional[Walkway]: El objeto de pasarela si se encuentra, de lo contrario None.
        """
        return self.db.execute(
            select(self.model).filter_by(name=name)
        ).scalars().first()

    def get_all(self) -> List[Walkway]:
        """
        Obtiene todas las pasarelas.
        """
        return self.db.execute(select(self.model)).scalars().all()

    def create(self, data: dict) -> Walkway:
        """
        Crea una nueva pasarela a partir de un diccionario de datos.
        """
        new_walkway = Walkway(**data)
        self.db.add(new_walkway)
        self.db.commit()
        self.db.refresh(new_walkway)
        return new_walkway

    def update(self, walkway_id: int, data: dict) -> Optional[Walkway]:
        """
        Actualiza una pasarela existente.
        """
        walkway = self.get_by_id(walkway_id)
        if not walkway:
            return None
        
        for key, value in data.items():
            setattr(walkway, key, value)
        
        self.db.commit()
        self.db.refresh(walkway)
        return walkway
    
    def delete(self, walkway_id: int) -> bool:
        """
        Elimina una pasarela por su ID.
        """
        walkway = self.get_by_id(walkway_id)
        if walkway:
            self.db.delete(walkway)
            self.db.commit()
            return True
        return False
