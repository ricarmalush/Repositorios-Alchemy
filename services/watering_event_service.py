# services/watering_event_service.py

from sqlalchemy.orm import Session
from typing import Optional, List
import datetime

# Importamos los repositorios que este servicio necesitará
from repositories.watering_event_repository import WateringEventRepository
from repositories.user_watering_schedule_repository import UserWateringScheduleRepository
from repositories.user_repository import UserRepository # Para obtener detalles del usuario si es necesario


class WateringEventService:
    def __init__(self, db: Session):
        self.watering_event_repo = WateringEventRepository(db)
        self.user_watering_schedule_repo = UserWateringScheduleRepository(db)
        self.user_repo = UserRepository(db) # Para validaciones o para enriquecer datos
        self.db = db

    def record_watering_event(self, event_data: dict) -> Optional[WateringEventRepository.model]:
        """
        Registra un nuevo evento de riego.
        event_data debe contener:
        'user_id', 'schedule_id', 'start_time', 'end_time', 'volume_liters', 'duration_minutes'
        """
        user_id = event_data['user_id']
        schedule_id = event_data['schedule_id']
        start_time = event_data['start_time']
        end_time = event_data['end_time']
        volume_liters = event_data['volume_liters']
        duration_minutes = event_data['duration_minutes']

        # 1. Validaciones de Negocio
        # A. Validar que el usuario existe
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"Usuario con ID {user_id} no encontrado.")

        # B. Validar que la programación de riego existe
        schedule = self.user_watering_schedule_repo.get_schedule_by_id(schedule_id)
        if not schedule:
            raise ValueError(f"Programación de riego con ID {schedule_id} no encontrada.")
        
        # C. Validar que el evento pertenece al usuario y a la programación correcta
        if schedule.user_id != user_id:
            raise ValueError(f"La programación {schedule_id} no pertenece al usuario {user_id}.")

        # D. Validar tiempos: start_time debe ser anterior a end_time
        if start_time >= end_time:
            raise ValueError("La hora de inicio del evento debe ser anterior a la hora de fin.")

        # E. Opcional: Validar que el evento ocurra dentro del rango de la programación
        # Esto es complejo porque un evento puede ser parte de una programación,
        # pero no tiene que coincidir exactamente. Podríamos validar si se superpone.
        # Por ahora, simplemente verificamos que la programación existe.

        # F. Validar que el volumen de agua y la duración sean positivos
        if volume_liters <= 0:
            raise ValueError("El volumen de agua debe ser un valor positivo.")
        if duration_minutes <= 0:
            raise ValueError("La duración del riego debe ser un valor positivo.")

        # 2. Llamar al repositorio para crear el evento
        try:
            new_event = self.watering_event_repo.create(event_data)
            return new_event
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Error al registrar el evento de riego: {e}")

    def get_event_by_id(self, event_id: int) -> Optional[WateringEventRepository.model]:
        """
        Obtiene un evento de riego por su ID.
        """
        return self.watering_event_repo.get_by_id(event_id)

    def get_events_for_user(self, user_id: int, start_date: Optional[datetime.date] = None, end_date: Optional[datetime.date] = None) -> List[WateringEventRepository.model]:
        """
        Obtiene los eventos de riego para un usuario específico, con filtros opcionales de fecha.
        """
        # Si un administrador consulta, no habría restricción de user_id.
        return self.watering_event_repo.get_events_for_user(user_id, start_date, end_date)

    def get_total_water_used(self, start_date: Optional[datetime.date] = None, end_date: Optional[datetime.date] = None) -> float:
        """
        Calcula el volumen total de agua utilizada en un rango de fechas.
        """
        # Este es un buen lugar para añadir lógica de agregación o permisos sobre los datos totales.
        return self.watering_event_repo.get_total_water_used(start_date, end_date)

    def get_events_by_schedule(self, schedule_id: int) -> List[WateringEventRepository.model]:
        """
        Obtiene todos los eventos de riego asociados a una programación específica.
        """
        return self.watering_event_repo.get_events_by_schedule(schedule_id)

    def get_recent_events(self, limit: int = 10) -> List[WateringEventRepository.model]:
        """
        Obtiene los eventos de riego más recientes (para un dashboard, por ejemplo).
        """
        return self.watering_event_repo.get_recent_events(limit)

    # Puedes añadir métodos para actualizar o eliminar eventos si tu lógica de negocio lo permite.
    # Por ejemplo, un evento podría ser "corregido" si se registró mal.
    # def update_event(self, event_id: int, update_data: dict) -> Optional[WateringEventRepository.model]:
    #     # Lógica de validación para update_data
    #     return self.watering_event_repo.update(event_id, update_data)

    # def delete_event(self, event_id: int) -> bool:
    #     # Lógica de confirmación antes de eliminar un registro histórico
    #     return self.watering_event_repo.delete(event_id)