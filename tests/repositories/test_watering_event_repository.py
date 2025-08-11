# Importamos los modelos necesarios para los tests
import datetime
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from database.base import Base
from database.models.user import User
from database.models.user_watering_schedule import UserWateringSchedule
from database.models.watering_event import WateringEvent
from database.models.access_schedule_rule import AccessScheduleRule
from database.models.user_type import UserType # Asegúrate de importar UserType
from database.models.walkway import Walkway # Asegúrate de importar Walkway

# Importamos el repositorio que vamos a testear
from repositories.watering_event_repository import WateringEventRepository

# Importamos el BaseRepository para asegurar que sus métodos están disponibles si no los testamos directamente
from repositories.base_repository import BaseRepository

# Fixture para la base de datos en memoria y sesión
@pytest.fixture(scope="function")
def watering_event_repo(db_session: Session) -> WateringEventRepository:
    """
    Proporciona una instancia del WateringEventRepository con una sesión de base de datos.
    """
    return WateringEventRepository(db_session)

# Fixture para crear un usuario de prueba (necesario para eventos de riego)
@pytest.fixture
def test_user(db_session: Session) -> User:
    """
    Crea y devuelve un usuario de prueba, asegurándose de que las dependencias de FK existan.
    """
    # Crea un UserType de prueba si no existe
    user_type = db_session.query(UserType).filter_by(name="Default Test UserType").first()
    if not user_type:
        user_type = UserType(name="Default Test UserType")
        db_session.add(user_type)
        db_session.flush() # Para obtener el ID si es autoincremental

    # Crea un Walkway de prueba si no existe
    walkway = db_session.query(Walkway).filter_by(name="Default Test Walkway").first()
    if not walkway:
        walkway = Walkway(name="Default Test Walkway", location_description="Default Test Location")
        db_session.add(walkway)
        db_session.flush() # Para obtener el ID

    # Crea un AccessScheduleRule de prueba si no existe
    access_rule = db_session.query(AccessScheduleRule).filter_by(rule_name="Default Test Rule").first()
    if not access_rule:
        access_rule = AccessScheduleRule(
            rule_name="Default Test Rule",
            day_of_week="Mon,Tue,Wed,Thu,Fri",
            start_time=datetime.time(8, 0, 0),
            end_time=datetime.time(17, 0, 0),
            user_type_id=user_type.id,
            walkway_id=walkway.id
        )
        db_session.add(access_rule)
        db_session.flush() # Para obtener el ID

    user = User(
        name="Test User Name",
        username="testuser",
        password_hash="hashedpassword",
        first_name="Test",
        last_name="User",
        email="test@example.com",
        phone_number="123456789",
        walkway_id=walkway.id, 
        user_type_id=user_type.id,
        access_schedule_rule_id=access_rule.id
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

# Fixture para crear una programación de riego de usuario (necesario para eventos de riego)
@pytest.fixture
def test_user_watering_schedule(db_session: Session, test_user: User) -> UserWateringSchedule:
    """
    Crea y devuelve una programación de riego de usuario de prueba.
    """
    schedule = UserWateringSchedule(
        user_id=test_user.id,
        scheduled_date=datetime.date.today(), 
        start_time=datetime.time(8, 0, 0),
        end_time=datetime.time(9, 0, 0),
        is_active=True
    )
    db_session.add(schedule)
    db_session.commit()
    db_session.refresh(schedule)
    return schedule

# -------------------------------------------------------------------------------------
# TESTS DE OPERACIONES CRUD BÁSICAS (HEREDADAS DE BaseRepository)
# -------------------------------------------------------------------------------------

def test_create_watering_event(watering_event_repo: WateringEventRepository, 
                               test_user: User, 
                               test_user_watering_schedule: UserWateringSchedule):
    """
    Verifica la creación de un nuevo evento de riego.
    """
    event = WateringEvent(
        user_id=test_user.id,
        schedule_id=test_user_watering_schedule.id,
        start_time=datetime.datetime(2023, 7, 26, 10, 0, 0),
        end_time=datetime.datetime(2023, 7, 26, 10, 30, 0),
        volume_liters=50.5,
        duration_minutes=30,
        walkway_id=test_user.walkway_id # AÑADIDO: walkway_id
    )
    created_event = watering_event_repo.create(event)
    assert created_event.id is not None
    assert created_event.user_id == test_user.id
    assert created_event.volume_liters == 50.5
    assert created_event.walkway_id == test_user.walkway_id

def test_get_watering_event_by_id(watering_event_repo: WateringEventRepository,
                                   test_user: User,
                                   test_user_watering_schedule: UserWateringSchedule):
    """
    Verifica la obtención de un evento de riego por su ID.
    """
    event = WateringEvent(
        user_id=test_user.id,
        schedule_id=test_user_watering_schedule.id,
        start_time=datetime.datetime(2023, 7, 26, 11, 0, 0),
        end_time=datetime.datetime(2023, 7, 26, 11, 45, 0),
        volume_liters=75.0,
        duration_minutes=45,
        walkway_id=test_user.walkway_id # AÑADIDO: walkway_id
    )
    created_event = watering_event_repo.create(event)

    fetched_event = watering_event_repo.get_by_id(created_event.id)
    assert fetched_event is not None
    assert fetched_event.id == created_event.id
    assert fetched_event.volume_liters == 75.0
    assert fetched_event.walkway_id == test_user.walkway_id

def test_get_all_watering_events(watering_event_repo: WateringEventRepository,
                                  test_user: User,
                                  test_user_watering_schedule: UserWateringSchedule):
    """
    Verifica la obtención de todos los eventos de riego.
    """
    event1 = WateringEvent(user_id=test_user.id, schedule_id=test_user_watering_schedule.id, start_time=datetime.datetime(2023, 7, 26, 9, 0, 0), end_time=datetime.datetime(2023, 7, 26, 9, 15, 0), volume_liters=20.0, duration_minutes=15, walkway_id=test_user.walkway_id) # AÑADIDO
    event2 = WateringEvent(user_id=test_user.id, schedule_id=test_user_watering_schedule.id, start_time=datetime.datetime(2023, 7, 27, 9, 0, 0), end_time=datetime.datetime(2023, 7, 27, 9, 15, 0), volume_liters=25.0, duration_minutes=15, walkway_id=test_user.walkway_id) # AÑADIDO
    watering_event_repo.create(event1)
    watering_event_repo.create(event2)

    all_events = watering_event_repo.get_all()
    assert len(all_events) == 2
    assert any(e.volume_liters == 20.0 for e in all_events)
    assert any(e.volume_liters == 25.0 for e in all_events)
    assert all(e.walkway_id == test_user.walkway_id for e in all_events) # Verificamos walkway_id

def test_update_watering_event(watering_event_repo: WateringEventRepository,
                                test_user: User,
                                test_user_watering_schedule: UserWateringSchedule):
    """
    Verifica la actualización de un evento de riego existente.
    """
    event = WateringEvent(user_id=test_user.id, schedule_id=test_user_watering_schedule.id, start_time=datetime.datetime(2023, 7, 26, 12, 0, 0), end_time=datetime.datetime(2023, 7, 26, 12, 30, 0), volume_liters=60.0, duration_minutes=30, walkway_id=test_user.walkway_id) # AÑADIDO
    created_event = watering_event_repo.create(event)

    updated_data = {"volume_liters": 65.5, "duration_minutes": 35}
    updated_event = watering_event_repo.update(created_event.id, updated_data)
    assert updated_event is not None
    assert updated_event.volume_liters == 65.5
    assert updated_event.duration_minutes == 35
    assert updated_event.walkway_id == test_user.walkway_id # Sigue siendo el mismo

def test_delete_watering_event(watering_event_repo: WateringEventRepository,
                               test_user: User,
                               test_user_watering_schedule: UserWateringSchedule):
    """
    Verifica la eliminación de un evento de riego.
    """
    event = WateringEvent(user_id=test_user.id, schedule_id=test_user_watering_schedule.id, start_time=datetime.datetime(2023, 7, 26, 13, 0, 0), end_time=datetime.datetime(2023, 7, 26, 13, 10, 0), volume_liters=10.0, duration_minutes=10, walkway_id=test_user.walkway_id) # AÑADIDO
    created_event = watering_event_repo.create(event)

    result = watering_event_repo.delete(created_event.id)
    assert result is True
    assert watering_event_repo.get_by_id(created_event.id) is None

def test_delete_non_existent_watering_event(watering_event_repo: WateringEventRepository):
    """
    Verifica que intentar eliminar un evento que no existe devuelve False.
    """
    result = watering_event_repo.delete(9999) # ID que no existe
    assert result is False

# -------------------------------------------------------------------------------------
# TESTS DE MÉTODOS ESPECÍFICOS DE WateringEventRepository
# -------------------------------------------------------------------------------------

def test_get_events_for_user(watering_event_repo: WateringEventRepository,
                             test_user: User,
                             test_user_watering_schedule: UserWateringSchedule):
    """
    Verifica la obtención de eventos para un usuario específico.
    """
    # Crear un segundo usuario y sus eventos para asegurar el filtrado
    # Asegúrate de que las dependencias para other_user también se crean si son NOT NULL
    other_user_type = watering_event_repo.db.query(UserType).filter_by(name="Other Test UserType").first()
    if not other_user_type:
        other_user_type = UserType(name="Other Test UserType")
        watering_event_repo.db.add(other_user_type)
        watering_event_repo.db.flush()

    other_walkway = watering_event_repo.db.query(Walkway).filter_by(name="Other Test Walkway").first()
    if not other_walkway:
        other_walkway = Walkway(name="Other Test Walkway", location_description="Other Test Location")
        watering_event_repo.db.add(other_walkway)
        watering_event_repo.db.flush()

    other_access_rule = watering_event_repo.db.query(AccessScheduleRule).filter_by(rule_name="Other Test Rule").first()
    if not other_access_rule:
        other_access_rule = AccessScheduleRule(
            rule_name="Other Test Rule",
            day_of_week="Tue",
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(18, 0, 0),
            user_type_id=other_user_type.id,
            walkway_id=other_walkway.id
        )
        watering_event_repo.db.add(other_access_rule)
        watering_event_repo.db.flush()

    other_user = User(
        name="Other User Name",
        username="otheruser",
        password_hash="otherhash",
        first_name="Other",
        last_name="User",
        email="other@example.com",
        phone_number="987654321",
        walkway_id=other_walkway.id, # Aseguramos que el otro usuario tiene un walkway_id
        user_type_id=other_user_type.id,
        access_schedule_rule_id=other_access_rule.id
    )
    watering_event_repo.db.add(other_user)
    watering_event_repo.db.commit()
    watering_event_repo.db.refresh(other_user)

    # Eventos para test_user
    event1_user1 = WateringEvent(user_id=test_user.id, schedule_id=test_user_watering_schedule.id, start_time=datetime.datetime(2023, 7, 20, 8, 0, 0), end_time=datetime.datetime(2023, 7, 20, 8, 30, 0), volume_liters=30, duration_minutes=30, walkway_id=test_user.walkway_id) # AÑADIDO
    event2_user1 = WateringEvent(user_id=test_user.id, schedule_id=test_user_watering_schedule.id, start_time=datetime.datetime(2023, 7, 21, 9, 0, 0), end_time=datetime.datetime(2023, 7, 21, 9, 45, 0), volume_liters=40, duration_minutes=45, walkway_id=test_user.walkway_id) # AÑADIDO
    
    # Evento para other_user
    event_user2 = WateringEvent(user_id=other_user.id, schedule_id=test_user_watering_schedule.id, start_time=datetime.datetime(2023, 7, 22, 10, 0, 0), end_time=datetime.datetime(2023, 7, 22, 10, 15, 0), volume_liters=10, duration_minutes=15, walkway_id=other_walkway.id) # AÑADIDO

    watering_event_repo.db.add_all([event1_user1, event2_user1, event_user2])
    watering_event_repo.db.commit()

    events_for_test_user = watering_event_repo.get_events_for_user(test_user.id)
    assert len(events_for_test_user) == 2
    assert all(e.user_id == test_user.id for e in events_for_test_user)
    assert events_for_test_user[0].volume_liters == 40 # El más reciente (asumiendo orden descendente por start_time en el repo)
    assert all(e.walkway_id == test_user.walkway_id for e in events_for_test_user) # Verificamos walkway_id

    # Test con filtro de fecha
    filtered_events = watering_event_repo.get_events_for_user(test_user.id, 
                                                            start_date=datetime.date(2023, 7, 21), 
                                                            end_date=datetime.date(2023, 7, 21))
    assert len(filtered_events) == 1
    assert filtered_events[0].volume_liters == 40
    assert filtered_events[0].walkway_id == test_user.walkway_id # Verificamos walkway_id


def test_get_events_by_schedule(watering_event_repo: WateringEventRepository,
                                 test_user: User,
                                 test_user_watering_schedule: UserWateringSchedule):
    """
    Verifica la obtención de eventos por una programación de riego específica.
    """
    # Crear un segundo schedule y sus eventos
    other_schedule = UserWateringSchedule(
        user_id=test_user.id, 
        scheduled_date=datetime.date.today(), 
        start_time=datetime.time(10,0,0), 
        end_time=datetime.time(11,0,0),
        is_active=True 
    )
    watering_event_repo.db.add(other_schedule)
    watering_event_repo.db.commit()
    watering_event_repo.db.refresh(other_schedule)

    event1_schedule1 = WateringEvent(user_id=test_user.id, schedule_id=test_user_watering_schedule.id, start_time=datetime.datetime(2023, 7, 20, 8, 0, 0), end_time=datetime.datetime(2023, 7, 20, 8, 30, 0), volume_liters=30, duration_minutes=30, walkway_id=test_user.walkway_id) # AÑADIDO
    event2_schedule1 = WateringEvent(user_id=test_user.id, schedule_id=test_user_watering_schedule.id, start_time=datetime.datetime(2023, 7, 21, 9, 0, 0), end_time=datetime.datetime(2023, 7, 21, 9, 45, 0), volume_liters=40, duration_minutes=45, walkway_id=test_user.walkway_id) # AÑADIDO
    
    event_schedule2 = WateringEvent(user_id=test_user.id, schedule_id=other_schedule.id, start_time=datetime.datetime(2023, 7, 22, 10, 0, 0), end_time=datetime.datetime(2023, 7, 22, 10, 15, 0), volume_liters=10, duration_minutes=15, walkway_id=test_user.walkway_id) # AÑADIDO

    watering_event_repo.db.add_all([event1_schedule1, event2_schedule1, event_schedule2])
    watering_event_repo.db.commit()

    events_for_schedule1 = watering_event_repo.get_events_by_schedule(test_user_watering_schedule.id)
    assert len(events_for_schedule1) == 2
    assert all(e.schedule_id == test_user_watering_schedule.id for e in events_for_schedule1)
    assert events_for_schedule1[0].volume_liters == 40 # Orden descendente
    assert all(e.walkway_id == test_user.walkway_id for e in events_for_schedule1) # Verificamos walkway_id

    events_for_schedule2 = watering_event_repo.get_events_by_schedule(other_schedule.id)
    assert len(events_for_schedule2) == 1
    assert events_for_schedule2[0].volume_liters == 10
    assert events_for_schedule2[0].walkway_id == test_user.walkway_id # Verificamos walkway_id

def test_get_recent_events(watering_event_repo: WateringEventRepository,
                           test_user: User,
                           test_user_watering_schedule: UserWateringSchedule):
    """
    Verifica la obtención de los eventos de riego más recientes.
    """
    # Crear varios eventos con diferentes horas
    event1 = WateringEvent(user_id=test_user.id, schedule_id=test_user_watering_schedule.id, start_time=datetime.datetime(2023, 7, 26, 8, 0, 0), end_time=datetime.datetime(2023, 7, 26, 8, 15, 0), volume_liters=10, duration_minutes=15, walkway_id=test_user.walkway_id) # AÑADIDO
    event2 = WateringEvent(user_id=test_user.id, schedule_id=test_user_watering_schedule.id, start_time=datetime.datetime(2023, 7, 26, 9, 0, 0), end_time=datetime.datetime(2023, 7, 26, 9, 15, 0), volume_liters=20, duration_minutes=15, walkway_id=test_user.walkway_id) # AÑADIDO
    event3 = WateringEvent(user_id=test_user.id, schedule_id=test_user_watering_schedule.id, start_time=datetime.datetime(2023, 7, 26, 10, 0, 0), end_time=datetime.datetime(2023, 7, 26, 10, 15, 0), volume_liters=30, duration_minutes=15, walkway_id=test_user.walkway_id) # AÑADIDO
    event4 = WateringEvent(user_id=test_user.id, schedule_id=test_user_watering_schedule.id, start_time=datetime.datetime(2023, 7, 26, 11, 0, 0), end_time=datetime.datetime(2023, 7, 26, 11, 15, 0), volume_liters=40, duration_minutes=15, walkway_id=test_user.walkway_id) # AÑADIDO
    
    watering_event_repo.db.add_all([event1, event2, event3, event4])
    watering_event_repo.db.commit()

    recent_events = watering_event_repo.get_recent_events(limit=2)
    assert len(recent_events) == 2
    assert recent_events[0].volume_liters == 40 # El más reciente
    assert recent_events[1].volume_liters == 30 # El segundo más reciente
    assert all(e.walkway_id == test_user.walkway_id for e in recent_events) # Verificamos walkway_id

    all_recent_events = watering_event_repo.get_recent_events(limit=100) # Más del total
    assert len(all_recent_events) == 4
    assert all(e.walkway_id == test_user.walkway_id for e in all_recent_events) # Verificamos walkway_id

def test_get_total_water_used(watering_event_repo: WateringEventRepository,
                             test_user: User,
                             test_user_watering_schedule: UserWateringSchedule):
    """
    Verifica el cálculo del volumen total de agua utilizado en un rango de fechas.
    """
    event1 = WateringEvent(user_id=test_user.id, schedule_id=test_user_watering_schedule.id, start_time=datetime.datetime(2023, 7, 25, 8, 0, 0), end_time=datetime.datetime(2023, 7, 25, 8, 15, 0), volume_liters=10.5, duration_minutes=15, walkway_id=test_user.walkway_id) # AÑADIDO
    event2 = WateringEvent(user_id=test_user.id, schedule_id=test_user_watering_schedule.id, start_time=datetime.datetime(2023, 7, 26, 9, 0, 0), end_time=datetime.datetime(2023, 7, 26, 9, 15, 0), volume_liters=20.0, duration_minutes=15, walkway_id=test_user.walkway_id) # AÑADIDO
    event3 = WateringEvent(user_id=test_user.id, schedule_id=test_user_watering_schedule.id, start_time=datetime.datetime(2023, 7, 27, 10, 0, 0), end_time=datetime.datetime(2023, 7, 27, 10, 15, 0), volume_liters=30.0, duration_minutes=15, walkway_id=test_user.walkway_id) # AÑADIDO
    event4 = WateringEvent(user_id=test_user.id, schedule_id=test_user_watering_schedule.id, start_time=datetime.datetime(2023, 7, 28, 11, 0, 0), end_time=datetime.datetime(2023, 7, 28, 11, 15, 0), volume_liters=40.0, duration_minutes=15, walkway_id=test_user.walkway_id) # AÑADIDO
    
    watering_event_repo.db.add_all([event1, event2, event3, event4])
    watering_event_repo.db.commit()

    # Test sin filtro de fecha (todos los eventos)
    total_all_events = watering_event_repo.get_total_water_used()
    assert total_all_events == (10.5 + 20.0 + 30.0 + 40.0)

    # Test con filtro de fecha (rango específico)
    total_filtered_events = watering_event_repo.get_total_water_used(
        start_date=datetime.date(2023, 7, 26),
        end_date=datetime.date(2023, 7, 27)
    )
    assert total_filtered_events == (20.0 + 30.0)

    # Test con un solo día
    total_single_day = watering_event_repo.get_total_water_used(
        start_date=datetime.date(2023, 7, 25),
        end_date=datetime.date(2023, 7, 25)
    )
    assert total_single_day == 10.5

    # Test con rango que no contiene eventos
    total_no_events = watering_event_repo.get_total_water_used(
        start_date=datetime.date(2024, 1, 1),
        end_date=datetime.date(2024, 1, 31)
    )
    assert total_no_events == 0.0

    # Test solo con start_date
    total_from_start = watering_event_repo.get_total_water_used(
        start_date=datetime.date(2023, 7, 27)
    )
    assert total_from_start == (30.0 + 40.0)

    # Test solo con end_date
    total_to_end = watering_event_repo.get_total_water_used(
        end_date=datetime.date(2023, 7, 26)
    )
    assert total_to_end == (10.5 + 20.0)
