# notification_repository.py

import logging
from typing import Optional, List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import desc

from database.models.notification import Notification

# Configuración de logging para una mejor visibilidad
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_notification(self, user_id: int, title: str, message: str, type: str) -> Notification:
        # Aquí se crearía la notificación usando el nuevo parámetro 'type'
        new_notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type, 
            is_read=False
        )
        self.db_session.add(new_notification)
        self.db_session.commit()
        self.db_session.refresh(new_notification)
        return new_notification

    def get_all_by_user_id(self, user_id: UUID, status: str = "all") -> List[Notification]:
        """
        Obtiene todas las notificaciones para un usuario, opcionalmente filtradas por estado.
        
        Args:
            user_id (UUID): El ID del usuario.
            status (str): "all", "read" o "unread" para filtrar.
            
        Returns:
            List[Notification]: Una lista de notificaciones.
        """
        query = self.db_session.query(Notification).filter_by(user_id=user_id)
        if status == "read":
            query = query.filter_by(is_read=True)
        elif status == "unread":
            query = query.filter_by(is_read=False)
        
        notifications = query.order_by(desc(Notification.created_at)).all()
        logger.info(f"Obtenidas {len(notifications)} notificaciones para el usuario: {user_id} con estado: {status}")
        return notifications

    def mark_as_read(self, notification_id: UUID) -> Optional[Notification]:
        """
        Marca una notificación específica como leída.
        
        Args:
            notification_id (UUID): El ID de la notificación.
            
        Returns:
            Optional[Notification]: La notificación actualizada, o None si no se encontró.
        """
        try:
            notification = self.db_session.query(Notification).filter_by(id=notification_id).first()
            if notification:
                notification.is_read = True
                self.db_session.commit()
                self.db_session.refresh(notification)
                logger.info(f"Notificación con ID: {notification_id} marcada como leída.")
            else:
                logger.warning(f"No se encontró ninguna notificación con ID: {notification_id} para marcar como leída.")
            return notification
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error al marcar la notificación con ID {notification_id} como leída: {e}")
            raise
    
    def mark_all_as_read(self, user_id: UUID) -> int:
        """
        Marca todas las notificaciones no leídas de un usuario como leídas.
        
        Args:
            user_id (UUID): El ID del usuario.
            
        Returns:
            int: El número de notificaciones actualizadas.
        """
        try:
            notifications = self.db_session.query(Notification).filter_by(user_id=user_id, is_read=False).all()
            for notification in notifications:
                notification.is_read = True
            self.db_session.commit()
            logger.info(f"{len(notifications)} notificaciones para el usuario {user_id} marcadas como leídas.")
            return len(notifications)
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error al marcar todas las notificaciones para el usuario {user_id} como leídas: {e}")
            raise

    def delete_notification(self, notification_id: UUID) -> bool:
        """
        Elimina una notificación por su ID.
        
        Args:
            notification_id (UUID): El ID de la notificación a eliminar.
            
        Returns:
            bool: True si la notificación fue eliminada, False si no se encontró.
        """
        try:
            notification = self.db_session.query(Notification).filter_by(id=notification_id).first()
            if notification:
                self.db_session.delete(notification)
                self.db_session.commit()
                logger.info(f"Notificación con ID: {notification_id} eliminada exitosamente.")
                return True
            logger.warning(f"No se encontró la notificación con ID: {notification_id} para eliminar.")
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error al eliminar la notificación con ID {notification_id}: {e}")
            return False
