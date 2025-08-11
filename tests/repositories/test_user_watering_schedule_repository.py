# test_user_watering_schedule_repository.py

from datetime import time
from uuid import uuid4
import pytest
import datetime
from sqlalchemy.orm import Session
from database.models.user_watering_schedule import UserWateringSchedule
from database.models.walkway import Walkway
from database.models.user import User
from database.models.access_schedule_rule import AccessScheduleRule
from database.models.user_type import UserType
from repositories.user_watering_schedule_repository import UserWateringScheduleRepository
from database.models.access_schedule_rule import AccessScheduleRule


# --- Fixtures de Entidades Básicas (sin dependencias cíclicas) ---

@pytest.fixture(scope="function")
def user_watering_schedule_repo(db_session: Session) -> UserWateringScheduleRepository:
    return UserWateringScheduleRepository(db_session)

@pytest.fixture(scope="function")
def user_type_fixture(db_session: Session) -> UserType:
    user_type = UserType(name="Admin")
    db_session.add(user_type)
    db_session.commit()
    db_session.refresh(user_type)
    return user_type

@pytest.fixture(scope="function")
def walkway_fixture(db_session: Session) -> Walkway:
    """
    Fixtura que crea un pasillo de prueba en la base de datos.
    """
    walkway = Walkway(
        name="Test Walkway",
        location_description="Main entrance",
    )
    db_session.add(walkway)
    db_session.commit()
    db_session.refresh(walkway)
    return walkway

@pytest.fixture(scope="function")
def user_fixture(
    db_session: Session,
    user_type_fixture: UserType,
    walkway_fixture: Walkway,
    access_schedule_rule_fixture: AccessScheduleRule
) -> User:
    user = User(
        name="Test Newname",
        first_name="fir_name",
        last_name="last_name",
        phone_number="123456789",
        username="Test User",
        email=f"test_user_{uuid4()}@example.com",
        password_hash="hashed_password",
        user_type_id=user_type_fixture.id,
        walkway_id=walkway_fixture.id,
        access_schedule_rule_id=access_schedule_rule_fixture.id,
    )
    db_session.add(user)
    db_session.commit()
    return user

# --- Fixtures de Entidades con Relaciones ---

@pytest.fixture(scope="function")
def access_schedule_rule_fixture(
    db_session: Session,
    user_type_fixture: UserType,
    walkway_fixture: Walkway
) -> AccessScheduleRule:
    rule = AccessScheduleRule(
        rule_name="Regla de Acceso Diaria",
        day_of_week="Mon,Tue,Wed,Thu,Fri",
        start_time=time(8, 0, 0),
        end_time=time(17, 0, 0),
        user_type_id=user_type_fixture.id,
        walkway_id=walkway_fixture.id
    )
    db_session.add(rule)
    db_session.commit()
    db_session.refresh(rule)
    return rule

@pytest.fixture(scope="function")
def schedule_fixture(db_session: Session, user_fixture: User) -> UserWateringSchedule:
    schedule = UserWateringSchedule(
        user_id=user_fixture.id,
        scheduled_date=datetime.date.today(),
        start_time=datetime.time(8, 0, 0),
        end_time=datetime.time(9, 0, 0),
    )
    db_session.add(schedule)
    db_session.commit()
    db_session.refresh(schedule)
    return schedule

# --- Tests ---

def test_create_schedule_success(user_watering_schedule_repo: UserWateringScheduleRepository, user_fixture: User, db_session: Session):
    schedule_data = {
        'user_id': user_fixture.id,
        'scheduled_date': datetime.date(2025, 8, 5),
        'start_time': datetime.time(8, 0, 0),
        'end_time': datetime.time(9, 0, 0)
    }

    new_schedule = user_watering_schedule_repo.create(schedule_data)

    assert new_schedule is not None
    assert new_schedule.user_id == user_fixture.id
    assert new_schedule.scheduled_date == datetime.date(2025, 8, 5)
    assert new_schedule.is_active is True
    
    db_schedule = db_session.get(UserWateringSchedule, new_schedule.id)
    assert db_schedule is not None
    assert db_schedule.start_time == datetime.time(8, 0, 0)


def test_get_by_id_success(user_watering_schedule_repo: UserWateringScheduleRepository, schedule_fixture: UserWateringSchedule):
    found_schedule = user_watering_schedule_repo.get_by_id(schedule_fixture.id)
    
    assert found_schedule is not None
    assert found_schedule.id == schedule_fixture.id
    assert found_schedule.user_id == schedule_fixture.user_id

def test_get_by_id_not_found(user_watering_schedule_repo: UserWateringScheduleRepository):
    non_existent_id = uuid4()
    found_schedule = user_watering_schedule_repo.get_by_id(non_existent_id)
    assert found_schedule is None

def test_get_schedules_for_user_without_date(user_watering_schedule_repo: UserWateringScheduleRepository, user_fixture: User, db_session: Session):
    today = datetime.date.today()
    schedule1 = UserWateringSchedule(user_id=user_fixture.id, scheduled_date=today, start_time=datetime.time(8,0), end_time=datetime.time(8,30))
    schedule2 = UserWateringSchedule(user_id=user_fixture.id, scheduled_date=today + datetime.timedelta(days=1), start_time=datetime.time(9,0), end_time=datetime.time(9,30))
    schedule3 = UserWateringSchedule(user_id=user_fixture.id, scheduled_date=today + datetime.timedelta(days=2), start_time=datetime.time(10,0), end_time=datetime.time(10,30))
    db_session.add_all([schedule1, schedule2, schedule3])
    db_session.commit()

    schedules = user_watering_schedule_repo.get_schedules_for_user(user_fixture.id, date=None)
    
    assert len(schedules) == 3
    assert schedules[0].start_time == datetime.time(8,0)

def test_get_schedules_for_user_with_date(user_watering_schedule_repo: UserWateringScheduleRepository, user_fixture: User, db_session: Session):
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    tomorrow = today + datetime.timedelta(days=1)
    schedule1 = UserWateringSchedule(user_id=user_fixture.id, scheduled_date=yesterday, start_time=datetime.time(8,0), end_time=datetime.time(8,30))
    schedule2 = UserWateringSchedule(user_id=user_fixture.id, scheduled_date=today, start_time=datetime.time(9,0), end_time=datetime.time(9,30))
    schedule3 = UserWateringSchedule(user_id=user_fixture.id, scheduled_date=tomorrow, start_time=datetime.time(10,0), end_time=datetime.time(10,30))
    db_session.add_all([schedule1, schedule2, schedule3])
    db_session.commit()

    schedules = user_watering_schedule_repo.get_schedules_for_user(user_fixture.id, date=today)
    
    assert len(schedules) == 1
    assert schedules[0].scheduled_date == today
    assert schedules[0].start_time == datetime.time(9,0)

def test_get_overlapping_schedules_found(user_watering_schedule_repo: UserWateringScheduleRepository, user_fixture: User, db_session: Session):
    now = datetime.datetime.now()
    schedule_existing = UserWateringSchedule(
        user_id=user_fixture.id,
        scheduled_date=now.date(),
        start_time=(now - datetime.timedelta(minutes=15)).time(),
        end_time=(now + datetime.timedelta(minutes=15)).time()
    )
    db_session.add(schedule_existing)
    db_session.commit()
    db_session.refresh(schedule_existing)

    overlapping_start_time = now
    overlapping_end_time = now + datetime.timedelta(minutes=30)
    
    overlapping_schedules = user_watering_schedule_repo.get_overlapping_schedules(
        user_id=user_fixture.id,
        start_time=overlapping_start_time,
        end_time=overlapping_end_time
    )

    assert len(overlapping_schedules) == 1
    assert overlapping_schedules[0].id == schedule_existing.id

def test_get_overlapping_schedules_not_found(user_watering_schedule_repo: UserWateringScheduleRepository, user_fixture: User):
    now = datetime.datetime.now()
    non_overlapping_start_time = now
    non_overlapping_end_time = now + datetime.timedelta(minutes=30)

    overlapping_schedules = user_watering_schedule_repo.get_overlapping_schedules(
        user_id=user_fixture.id,
        # FIX: Se eliminó el argumento 'date'.
        start_time=non_overlapping_start_time,
        end_time=non_overlapping_end_time
    )
    
    assert len(overlapping_schedules) == 0

def test_get_overlapping_schedules_with_exclusion(user_watering_schedule_repo: UserWateringScheduleRepository, user_fixture: User, db_session: Session):
    now = datetime.datetime.now()
    schedule_to_update = UserWateringSchedule(
        user_id=user_fixture.id,
        scheduled_date=now.date(),
        start_time=(now - datetime.timedelta(minutes=15)).time(),
        end_time=(now + datetime.timedelta(minutes=15)).time()
    )
    db_session.add(schedule_to_update)
    db_session.commit()
    db_session.refresh(schedule_to_update)

    overlapping_start_time = now
    overlapping_end_time = now + datetime.timedelta(minutes=30)

    overlapping_schedules = user_watering_schedule_repo.get_overlapping_schedules(
        user_id=user_fixture.id,
        start_time=overlapping_start_time,
        end_time=overlapping_end_time,
        exclude_schedule_id=schedule_to_update.id
    )

    assert len(overlapping_schedules) == 0

def test_get_upcoming_schedules_found(user_watering_schedule_repo: UserWateringScheduleRepository, user_fixture: User, db_session: Session):
    now = datetime.datetime.now()
    
    past_schedule = UserWateringSchedule(
        user_id=user_fixture.id,
        scheduled_date=(now - datetime.timedelta(days=1)).date(),
        start_time=datetime.time(8, 0, 0),
        end_time=datetime.time(8, 30, 0)
    )
    
    future_schedule1 = UserWateringSchedule(
        user_id=user_fixture.id,
        scheduled_date=(now + datetime.timedelta(days=1)).date(),
        start_time=datetime.time(9, 0, 0),
        end_time=datetime.time(10, 0, 0)
    )
    future_schedule2 = UserWateringSchedule(
        user_id=user_fixture.id,
        scheduled_date=(now + datetime.timedelta(days=2)).date(),
        start_time=datetime.time(10, 0, 0),
        end_time=datetime.time(11, 0, 0)
    )
    db_session.add_all([past_schedule, future_schedule1, future_schedule2])
    db_session.commit()

    upcoming_schedules = user_watering_schedule_repo.get_upcoming_schedules()
    
    assert len(upcoming_schedules) == 2
    assert future_schedule1 in upcoming_schedules
    assert future_schedule2 in upcoming_schedules
    assert past_schedule not in upcoming_schedules
    
    assert upcoming_schedules[0].scheduled_date == future_schedule1.scheduled_date
    assert upcoming_schedules[1].scheduled_date == future_schedule2.scheduled_date


def test_get_schedules_for_walkway_on_date(user_watering_schedule_repo: UserWateringScheduleRepository, user_fixture: User, db_session: Session):
    """
    Test que verifica que se pueden obtener las programaciones de riego para un
    pasillo en una fecha específica.

    El test falla en la línea `db_session.commit()` porque el objeto User
    está siendo creado sin el campo 'name', el cual tiene una restricción
    'NOT NULL'. Se añade el campo 'name' para corregir el error.
    """
    # Se crea un nuevo pasillo (walkway)
    other_walkway = Walkway(name="Other Walkway", location_description="Another Test Location")
    db_session.add(other_walkway)
    db_session.flush()

    # Se crea un nuevo usuario asociado al pasillo, incluyendo el campo 'name'
    other_user = User(
        name="Other Test User", 
        username="Other User",
        email=f"other.user_{uuid4()}@example.com",
        password_hash="hashed_password",
        first_name="Other",
        last_name="User",
        user_type_id=user_fixture.user_type_id,
        walkway_id=other_walkway.id,
        access_schedule_rule_id=user_fixture.access_schedule_rule_id
    )
    db_session.add(other_user)
    db_session.commit()

    # Se crea una programación de riego para el nuevo usuario
    start_time = datetime.datetime(2025, 8, 4, 10, 0, 0)
    end_time = datetime.datetime(2025, 8, 4, 11, 0, 0)


def test_update_schedule_success(user_watering_schedule_repo: UserWateringScheduleRepository, schedule_fixture: UserWateringSchedule, db_session: Session):
    update_data = {
        'start_time': datetime.time(11, 0, 0),
        'end_time': datetime.time(12, 0, 0)
    }

    updated_schedule = user_watering_schedule_repo.update(schedule_fixture.id, update_data)

    assert updated_schedule is not None
    assert updated_schedule.id == schedule_fixture.id
    assert updated_schedule.start_time == datetime.time(11, 0, 0)
    assert updated_schedule.end_time == datetime.time(12, 0, 0)
    
    db_session.refresh(schedule_fixture)
    assert schedule_fixture.start_time == datetime.time(11, 0, 0)

def test_delete_schedule_success(user_watering_schedule_repo: UserWateringScheduleRepository, schedule_fixture: UserWateringSchedule, db_session: Session):
    result = user_watering_schedule_repo.delete(schedule_fixture.id)
    
    assert result is True
    deleted_schedule = db_session.get(UserWateringSchedule, schedule_fixture.id)
    assert deleted_schedule is None

def test_delete_schedule_not_found(user_watering_schedule_repo: UserWateringScheduleRepository):
    non_existent_id = uuid4()
    result = user_watering_schedule_repo.delete(non_existent_id)
    assert result is False
