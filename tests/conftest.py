import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import sys
import os

# --- MENSAJE DE DEPURACIÓN CRÍTICO ---
# Si ves este mensaje en la consola, significa que pytest está cargando este archivo.
print("--- [ DEBUG ] conftest.py está siendo cargado. ---")

# --- CORRECCIÓN FINAL PARA EL PROBLEMA DE IMPORTACIÓN ---
# Añade la raíz del proyecto (la carpeta 'SQLALCHEMY_REGADIO')
# al sys.path para que pytest pueda encontrar los módulos como 'shared', 'repositories', etc.
# El error 'ModuleNotFoundError' proviene de aquí si esta corrección falla.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"--- [ DEBUG ] Añadiendo '{project_root}' a sys.path. ---")
else:
    print(f"--- [ DEBUG ] '{project_root}' ya está en sys.path. ---")
# ----------------------------------------------------


# Importar todos los modelos para que la base de datos los conozca
from database.base import Base
from database.models.access_schedule_rule import AccessScheduleRule
from database.models.user_type import UserType
from database.models.walkway import Walkway
from database.models.user import User
from database.models.user_watering_schedule import UserWateringSchedule
from database.models.watering_event import WateringEvent
from database.models.notification import Notification

# Importar repositorios y servicios para las fixtures
from repositories.user_repository import UserRepository
from repositories.user_type_repository import UserTypeRepository
from repositories.walkway_repository import WalkwayRepository
from repositories.access_schedule_rule_repository import AccessScheduleRuleRepository
from repositories.notification_repository import NotificationRepository

from services.user_type_service import UserTypeService
from services.walkway_service import WalkwayService
from services.access_schedule_rule_service import AccessScheduleRuleService
from services.notification_service import NotificationService


@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Fixture que proporciona una sesión de base de datos aislada para cada función de test.
    """
    engine = create_engine("sqlite:///:memory:")
    
    # Crea todas las tablas
    Base.metadata.create_all(engine)
    
    db: Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)


# --- FIXTURES DE REPOSITORIO ---
@pytest.fixture(scope="function")
def user_repo(db_session: Session) -> UserRepository:
    """Fixture para el repositorio de User."""
    return UserRepository(db_session)

@pytest.fixture(scope="function")
def user_type_repo(db_session: Session) -> UserTypeRepository:
    """Fixture para el repositorio de UserType."""
    return UserTypeRepository(db_session)

@pytest.fixture(scope="function")
def walkway_repo(db_session: Session) -> WalkwayRepository:
    """Fixture para el repositorio de Walkway."""
    return WalkwayRepository(db_session)

@pytest.fixture(scope="function")
def access_rule_repo(db_session: Session) -> AccessScheduleRuleRepository:
    """Fixture para el repositorio de AccessScheduleRule."""
    return AccessScheduleRuleRepository(db_session)

@pytest.fixture(scope="function")
def notification_repo(db_session: Session) -> NotificationRepository:
    """Fixture para el repositorio de Notification."""
    return NotificationRepository(db_session)


# --- FIXTURES DE SERVICIO (UNIFICADAS) ---
@pytest.fixture(scope="function")
def access_rule_service(db_session: Session) -> AccessScheduleRuleService:
    """Fixture para el servicio de AccessScheduleRule."""
    # Se utiliza 'db=' como argumento, no 'session='
    return AccessScheduleRuleService(db=db_session)

@pytest.fixture(scope="function")
def user_type_service(db_session: Session) -> UserTypeService:
    """Fixture para el servicio de UserType."""
    # Se utiliza 'db=' como argumento, no 'session='
    return UserTypeService(db=db_session)

@pytest.fixture(scope="function")
def walkway_service(db_session: Session) -> WalkwayService:
    """Fixture para el servicio de Walkway."""
    # Se utiliza 'db=' como argumento, no 'session='
    return WalkwayService(db=db_session)

@pytest.fixture(scope="function")
def notification_service(db_session: Session) -> NotificationService:
    """Fixture para el servicio de Notification."""
    # Se utiliza 'db=' como argumento, no 'session='
    return NotificationService(db=db_session)
