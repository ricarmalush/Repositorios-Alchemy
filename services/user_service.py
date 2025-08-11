# services/user_service.py

from sqlalchemy.orm import Session
from typing import Optional, List

# Importamos los repositorios que este servicio necesitará
from repositories.user_repository import UserRepository
from repositories.user_type_repository import UserTypeRepository # Necesario para verificar el rol
from repositories.user_watering_schedule_repository import UserWateringScheduleRepository
from repositories.watering_event_repository import WateringEventRepository
from repositories.notification_repository import NotificationRepository

# Modelos para tipificación
from database.models.user import User

# Intanciamos los repositorios
class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.user_type_repo = UserTypeRepository(db) 
        self.user_watering_schedule_repo = UserWateringScheduleRepository(db)
        self.watering_event_repo = WateringEventRepository(db)
        self.notification_repo = NotificationRepository(db) 
        self.db = db

    def create_user(
        self,
        name:str,
        username: str,
        password_hash: str,
        email: str,
        first_name: str,
        last_name: str,
        walkway_id: int,
        user_type_id: int,
        phone_number: Optional[str] = None,
        access_schedule_rule_id: Optional[int] = None,
        creating_user_id: Optional[int] = None 
    ) -> Optional[User]:
        """
        Crea un nuevo usuario.
        Añadimos una validación de permiso: solo 'Admin' puede crear usuarios de cierto tipo
        (o cualquier usuario si no es 'Admin' el tipo a crear).
        """
        # 1. Validaciones de Negocio
        # Validar unicidad del username y email
        if self.user_repo.get_by_username(username):
            raise ValueError(f"Ya existe un usuario con el nombre de usuario '{username}'.")
        if self.user_repo.get_by_email(email):
            raise ValueError(f"Ya existe un usuario con el email '{email}'.")
        
        # Validar que user_type_id y walkway_id existen
        user_type = self.user_type_repo.get_by_id(user_type_id)
        if not user_type:
            raise ValueError(f"Tipo de usuario con ID {user_type_id} no encontrado.")
        # Aquí necesitarías un WalkwayRepository para validar walkway_id
        # from repositories.walkway_repository import WalkwayRepository
        # walkway_repo = WalkwayRepository(self.db)
        # if not walkway_repo.get_by_id(walkway_id):
        #     raise ValueError(f"Andador con ID {walkway_id} no encontrado.")

        # Lógica de autorización para la creación de usuarios
        if creating_user_id:
            creating_user_type = self._get_user_type_name(creating_user_id)
            if creating_user_type != "Admin" and user_type.name == "Admin":
                raise PermissionError("Solo los administradores pueden crear usuarios con rol 'Admin'.")
            # Podrías añadir más reglas: un "User" no puede crear a nadie, solo un "Manager" puede crear "User", etc.
            # En este ejemplo, si no es 'Admin', puede crear cualquier rol excepto 'Admin'.

        user_data = {
            'name':name,
            'username': username,
            'password_hash': password_hash,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'walkway_id': walkway_id,
            'user_type_id': user_type_id,
            'phone_number': phone_number,
            'access_schedule_rule_id': access_schedule_rule_id
        }
        
        try:
            new_user = self.user_repo.create(user_data)
            return new_user
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Error al crear el usuario: {e}")

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.user_repo.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.user_repo.get_by_username(username)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.user_repo.get_by_email(email)

    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.user_repo.get_all(skip=skip, limit=limit)

    def update_user(self, user_id: int, update_data: dict, performing_user_id: int) -> Optional[User]:
        """
        Actualiza un usuario existente.
        Permite a los usuarios actualizar su propia información.
        Solo los administradores pueden actualizar la información de otros usuarios o cambiar el user_type_id.
        """
        user_to_update = self.user_repo.get_by_id(user_id)
        if not user_to_update:
            raise ValueError(f"Usuario con ID {user_id} no encontrado.")
        
        performing_user_type_name = self._get_user_type_name(performing_user_id)

        # Si el usuario NO es admin y no está actualizando su propia cuenta
        if performing_user_type_name != "Admin" and user_id != performing_user_id:
            raise PermissionError("No tienes permiso para actualizar la información de otros usuarios.")
        
        # Si NO es admin, no puede cambiar user_type_id de nadie (ni el suyo)
        if performing_user_type_name != "Admin" and 'user_type_id' in update_data:
             raise PermissionError("No tienes permiso para cambiar el tipo de usuario (rol).")
        
        # Si es admin, pero intenta cambiar su propio user_type_id a algo que no sea admin (opcional)
        if performing_user_type_name == "Admin" and user_id == performing_user_id and 'user_type_id' in update_data:
            new_user_type = self.user_type_repo.get_by_id(update_data['user_type_id'])
            if new_user_type and new_user_type.name != "Admin":
                raise PermissionError("Un administrador no puede degradar su propio rol.")

        try:
            updated_user = self.user_repo.update(user_id, update_data)
            return updated_user
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Error al actualizar el usuario: {e}")

    def delete_user(self, user_id: int, performing_user_id: int) -> bool:
        """
        Elimina un usuario.
        Solo permitido para administradores. Un administrador no puede eliminarse a sí mismo.
        """
        user_to_delete = self.user_repo.get_by_id(user_id)
        if not user_to_delete:
            return False # O lanzar un ValueError si prefieres

        performing_user_type_name = self._get_user_type_name(performing_user_id)

        # Lógica de autorización: Solo 'Admin' puede eliminar usuarios
        if performing_user_type_name != "Admin":
            raise PermissionError("Solo los administradores pueden eliminar usuarios.")

        # No permitir que un administrador se elimine a sí mismo
        if user_id == performing_user_id:
            raise ValueError("Un administrador no puede eliminarse a sí mismo.")

        # Lógica de negocio para manejar las relaciones (cascada, reasignación, etc.)
        # Antes de eliminar el usuario, hay que manejar sus dependencias (UserWateringSchedule, WateringEvent, Notification)
        # Esto es crucial para la integridad de los datos.
        
        # 1. Eliminar o reasignar UserWateringSchedules asociados
        user_schedules = self.user_watering_schedule_repo.get_schedules_by_user_id(user_id)
        for schedule in user_schedules:
            self.user_watering_schedule_repo.delete(schedule.id)
            
        # 2. Eliminar WateringEvents asociados
        user_events = self.watering_event_repo.get_events_by_user_id(user_id)
        for event in user_events:
            self.watering_event_repo.delete(event.id)

        # 3. Eliminar Notificaciones asociadas
        user_notifications = self.notification_repo.get_notifications_for_user(user_id)
        for notification in user_notifications:
            self.notification_repo.delete(notification.id)

        try:
            is_deleted = self.user_repo.delete(user_id)
            return is_deleted
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Error al eliminar el usuario: {e}")

    def _get_user_type_name(self, user_id: int) -> Optional[str]:
        """
        Método auxiliar para obtener el nombre del tipo de usuario (rol) dado un user_id.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None # O raise ValueError("Usuario no encontrado")
        user_type = self.user_type_repo.get_by_id(user.user_type_id)
        return user_type.name if user_type else None