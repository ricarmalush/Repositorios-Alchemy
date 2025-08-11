# backend/SQLALCHEMY_REGADIO/repositories/user_repository.py

from typing import Dict, Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models.user import User


class UserRepository:
    """
    Repositorio para la gestión de usuarios en la base de datos.
    """

    def __init__(self, db: Session):
        """
        Inicializa el repositorio de usuarios.

        Args:
            db (Session): La sesión de la base de datos de SQLAlchemy.
        """
        # La corrección principal aquí es usar `self.db` para almacenar la sesión.
        # Los métodos de la clase ahora también se corregirán para usar `self.db`
        # en lugar de `self.session`.
        self.db = db

    def create(self, user_data: Dict[str, Any]) -> User:
        """
        Crea un nuevo usuario en la base de datos.

        Args:
            user_data (Dict[str, Any]): Un diccionario con los datos del usuario.

        Returns:
            User: El objeto de usuario creado.
        """
        new_user = User(**user_data)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Obtiene un usuario por su ID.

        Args:
            user_id (int): El ID del usuario.

        Returns:
            Optional[User]: El objeto de usuario si se encuentra, de lo contrario None.
        """
        return self.db.execute(
            select(User).filter_by(id=user_id)
        ).scalar_one_or_none()

    def get_by_username(self, username: str) -> Optional[User]:
        """
        Obtiene un usuario por su nombre de usuario.

        Args:
            username (str): El nombre de usuario.

        Returns:
            Optional[User]: El objeto de usuario si se encuentra, de lo contrario None.
        """
        # CORRECCIÓN: Usamos `self.db` en lugar de `self.session` para acceder a la sesión
        return self.db.execute(select(User).filter_by(username=username)).scalar_one_or_none()

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Obtiene un usuario por su dirección de correo electrónico.

        Args:
            email (str): El email del usuario.

        Returns:
            Optional[User]: El objeto de usuario si se encuentra, de lo contrario None.
        """
        # CORRECCIÓN: Usamos `self.db` en lugar de `self.session` para acceder a la sesión
        return self.db.execute(select(User).filter_by(email=email)).scalar_one_or_none()

    def update(self, user_id: int, update_data: Dict[str, Any]) -> Optional[User]:
        """
        Actualiza un usuario existente.

        Args:
            user_id (int): El ID del usuario a actualizar.
            update_data (Dict[str, Any]): Un diccionario con los datos a actualizar.

        Returns:
            Optional[User]: El objeto de usuario actualizado si se encuentra, de lo contrario None.
        """
        user = self.get_by_id(user_id)
        if user:
            for key, value in update_data.items():
                setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
            return user
        return None

    def delete(self, user_id: int) -> bool:
        """
        Elimina un usuario de la base de datos.

        Args:
            user_id (int): El ID del usuario a eliminar.

        Returns:
            bool: True si el usuario fue eliminado, de lo contrario False.
        """
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
