# services/notification_service.py

from sqlalchemy.orm import Session
from typing import Optional, List
import datetime

# Importamos los repositorios que este servicio necesitará
from repositories.notification_repository import NotificationRepository
from repositories.user_repository import UserRepository # Para validar el user_id y obtener detalles del usuario

# Excepciones y mensajes de error personalizados
from Core.exceptions import NotFoundError, OperationFailedError, EmptyValueError
from Core.error_messages import GeneralErrors

# Modelos (opcional para tipificación o DTOs)
from database.models.notification import Notification


class NotificationService:
    """
    Servicio para manejar la lógica de negocio relacionada con las notificaciones.
    """
    def __init__(self, db: Session):
        self.notification_repo = NotificationRepository(db)
        self.user_repo = UserRepository(db) # Para validar que el user_id existe
        self.db = db

    def create_notification(self, user_id: int, title: str, message: str, type: Optional[str] = "info") -> Optional[Notification]:
        """
        Crea una nueva notificación para un usuario, con un título y un mensaje.
        Args:
            user_id (int): El ID del usuario al que se envía la notificación.
            title (str): El título de la notificación.
            message (str): El contenido del mensaje de la notificación.
            type (str): El tipo de notificación (ej. "info", "warning", "error", "success").
        """
        # 1. Validaciones de Negocio usando las excepciones personalizadas
        user = self.user_repo.get_by_id(user_id)
        if not user:
            # Lanzamos una NotFoundError si el usuario no existe.
            raise NotFoundError(entity_name="Usuario", entity_id=user_id)
        
        if not title or len(title.strip()) == 0:
            # Lanzamos una EmptyValueError si el título está vacío.
            raise EmptyValueError(field_name="título")

        if not message or len(message.strip()) == 0:
            # Lanzamos una EmptyValueError si el mensaje está vacío.
            raise EmptyValueError(field_name="mensaje")
        
        # Validar el 'type' de notificación
        valid_types = ["info", "warning", "error", "success", "system"]
        if type not in valid_types:
            print(f"Advertencia: Tipo de notificación '{type}' no reconocido. Usando 'info' por defecto.")
            type = "info"

        # 2. Llamar al repositorio para crear la notificación
        try:
            new_notification = self.notification_repo.create_notification(
                user_id=user_id,
                title=title,
                message=message,
                type=type
            )
            return new_notification
        except Exception as e:
            # En caso de un fallo inesperado, hacemos rollback y lanzamos una excepción de operación fallida.
            self.db.rollback()
            raise OperationFailedError(
                entity_name="notificación",
                operation="creación",
                original_exception=e
            )

    def get_notifications_for_user(
        self, 
        user_id: int, 
        is_read: Optional[bool] = None, 
        start_date: Optional[datetime.datetime] = None, 
        end_date: Optional[datetime.datetime] = None
    ) -> List[Notification]:
        """
        Obtiene las notificaciones para un usuario específico, con filtros opcionales.
        """
        return self.notification_repo.get_notifications_for_user(user_id, is_read, start_date, end_date)

    def mark_notification_as_read(self, notification_id: int) -> Optional[Notification]:
        """
        Marca una notificación específica como leída.
        """
        return self.notification_repo.mark_as_read(notification_id)

    def mark_all_user_notifications_as_read(self, user_id: int) -> int:
        """
        Marca todas las notificaciones no leídas de un usuario como leídas.
        """
        return self.notification_repo.mark_all_as_read_for_user(user_id)

    def get_unread_count_for_user(self, user_id: int) -> int:
        """
        Obtiene el número de notificaciones no leídas para un usuario.
        """
        return self.notification_repo.get_unread_notifications_count_for_user(user_id)

    def delete_notification(self, notification_id: int) -> bool:
        """
        Elimina una notificación por su ID.
        """
        try:
            return self.notification_repo.delete(notification_id)
        except Exception as e:
            # En caso de un fallo inesperado, hacemos rollback y lanzamos una excepción de operación fallida.
            self.db.rollback()
            raise OperationFailedError(
                entity_name="notificación",
                operation="eliminación",
                original_exception=e
            )

