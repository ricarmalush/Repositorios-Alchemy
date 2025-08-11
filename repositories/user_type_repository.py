# repositories/user_type_repository.py

from typing import Optional
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import select

# Importamos el modelo UserType
from database.models.user_type import UserType

# Importamos nuestro BaseRepository genérico
from .base_repository import BaseRepository


class UserTypeRepository(BaseRepository[UserType]):
    """
    Repositorio específico para el modelo UserType, heredando todas las operaciones CRUD básicas
    del BaseRepository. No necesita métodos específicos adicionales por ahora.
    """
    def __init__(self, db: Session):
        super().__init__(db, UserType) # Llama al constructor de BaseRepository, pasándole el modelo UserType

    # No se necesitan métodos específicos adicionales más allá de los provistos por BaseRepository
    # (get_by_id, create, update, delete, get_all, count_all)
    # Sin embargo, podríamos añadir uno para buscar por nombre si fuera necesario, por ejemplo:
    def get_by_name(self, name: str) -> Optional[UserType]:
        """
        Obtiene un tipo de usuario por su nombre.
        """
        return self.db.execute(select(UserType).filter_by(name=name)).scalar_one_or_none()