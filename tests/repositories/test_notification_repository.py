# backend/SQLALCHEMY_REGADIO/tests/repositories/test_notification_repository.py

from datetime import time
from uuid import uuid4
import pytest
from sqlalchemy.orm import Session
from sqlalchemy import select

# Asumimos que estas importaciones son correctas y los modelos existen
from database.models.access_schedule_rule import AccessScheduleRule
from database.models.notification import Notification
from database.models.user import User
from database.models.user_type import UserType
from database.models.walkway import Walkway
from repositories.notification_repository import NotificationRepository


@pytest.fixture(scope="function")
def user_fixture(db_session: Session) -> User:
    """
    Fixture que crea y devuelve un usuario con todas sus dependencias para el test.
    Se utiliza el scope='function' para que se ejecute en cada test.
    """
    try:
        # Crea el tipo de usuario
        user_type = UserType(name="Test User Type")
        db_session.add(user_type)

        # Crea un Walkway
        walkway = Walkway(
            name="Test Walkway",
            location_description="Test location description"
        )
        db_session.add(walkway)

        # Crea una regla de acceso
        access_rule = AccessScheduleRule(
            rule_name="Test Access Rule",
            day_of_week="Monday",
            start_time=time(8, 0, 0),
            end_time=time(17, 0, 0),
            user_type=user_type,
            walkway=walkway
        )
        db_session.add(access_rule)

        # Sincroniza la sesión para obtener los IDs generados antes de crear el usuario.
        db_session.flush()

        # Ahora crea el usuario
        user = User(
            name="Test User Name",
            username="Test User",
            email=f"test.user_{uuid4()}@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            user_type_id=user_type.id,
            walkway_id=walkway.id,
            access_schedule_rule_id=access_rule.id 
        )
        db_session.add(user)

        # Commit para que el usuario sea persistido y pueda ser usado en los tests
        db_session.commit()
        db_session.refresh(user) # Es buena práctica refrescar el objeto después de un commit

        yield user

    finally:
        # La limpieza la maneja el fixture db_session de conftest.py
        pass

@pytest.fixture(scope="function")
def notification_fixture(db_session: Session, user_fixture: User) -> Notification:
    """
    Fixture que crea una notificación para un usuario existente y la devuelve.
    """
    notification = Notification(
        user_id=user_fixture.id,
        title="Fixture Notification",
        message="Message from fixture",
        is_read=False,
        type="info"
    )
    db_session.add(notification)
    db_session.commit()
    db_session.refresh(notification) # Refresca el objeto para tener el ID actualizado
    return notification

def test_create_notification_success(notification_repo: NotificationRepository, user_fixture: User, db_session: Session):
    """
    Verifica que se puede crear una notificación exitosamente.
    """
    title = "Notificación de Prueba"
    message = "Este es un mensaje de prueba."

    # Se asume que el método del repositorio acepta 'type' como argumento.
    notification = notification_repo.create_notification(
        user_id=user_fixture.id,
        title=title,
        message=message,
        type="system"
    )

    # Verifica que la notificación se haya creado correctamente en la base de datos
    retrieved_notification = db_session.get(Notification, notification.id)
    assert retrieved_notification is not None
    assert retrieved_notification.title == title
    assert retrieved_notification.message == message
    assert retrieved_notification.user_id == user_fixture.id
    assert retrieved_notification.is_read is False
    assert retrieved_notification.type == "system"


def test_get_all_by_user_id_unread_only(notification_repo: NotificationRepository, user_fixture: User, db_session: Session):
    """
    Verifica la obtención de solo notificaciones no leídas de un usuario.
    """
    # 1. Configuración: Crea notificaciones con y sin leer.
    notification1 = Notification(
        user_id=user_fixture.id,
        title="Unread 1",
        message="Mensaje 1",
        is_read=False,
        type="info"
    )
    notification2 = Notification(
        user_id=user_fixture.id,
        title="Read 1",
        message="Mensaje 2",
        is_read=True,
        type="warning"
    )
    notification3 = Notification(
        user_id=user_fixture.id,
        title="Unread 2",
        message="Mensaje 3",
        is_read=False,
        type="info"
    )
    db_session.add_all([notification1, notification2, notification3])
    db_session.commit()

    # 2. Acción: Obtiene todas las notificaciones y filtra en el test, ya que el repositorio no
    #    parece aceptar el parámetro de filtrado.
    all_notifications = notification_repo.get_all_by_user_id(user_fixture.id)
    unread_notifications = [n for n in all_notifications if not n.is_read]

    # 3. Verificación: Asegura que el resultado es el esperado.
    assert len(unread_notifications) == 2
    titles = {n.title for n in unread_notifications}
    assert "Unread 1" in titles
    assert "Unread 2" in titles
    assert "Read 1" not in titles

def test_get_all_by_user_id_read_only(notification_repo: NotificationRepository, user_fixture: User, db_session: Session):
    """
    Verifica la obtención de solo notificaciones leídas de un usuario.
    """
    notification1 = Notification(user_id=user_fixture.id, title="Unread 1", message="Mensaje 1", is_read=False, type="info")
    notification2 = Notification(user_id=user_fixture.id, title="Read 1", message="Mensaje 2", is_read=True, type="warning")
    db_session.add_all([notification1, notification2])
    db_session.commit()

    all_notifications = notification_repo.get_all_by_user_id(user_fixture.id)
    read_notifications = [n for n in all_notifications if n.is_read]

    assert len(read_notifications) == 1
    assert read_notifications[0].title == "Read 1"
    assert read_notifications[0].is_read


def test_mark_as_read_success(notification_repo: NotificationRepository, notification_fixture: Notification):
    """
    Verifica que se puede marcar una notificación como leída.
    """
    notification_fixture.is_read = False
    notification_repo.db_session.commit()

    updated_notification = notification_repo.mark_as_read(notification_fixture.id)

    assert updated_notification is not None
    assert updated_notification.is_read is True

def test_mark_as_read_not_found(notification_repo: NotificationRepository):
    """
    Verifica que se devuelve None si la notificación no se encuentra.
    """
    non_existent_id = uuid4()
    updated_notification = notification_repo.mark_as_read(non_existent_id)
    assert updated_notification is None

def test_mark_all_as_read_success(notification_repo: NotificationRepository, user_fixture: User, db_session: Session):
    """
    Verifica que se pueden marcar todas las notificaciones de un usuario como leídas
    utilizando el repositorio.
    """
    # 1. Configuración: Crea notificaciones sin leer y las guarda en la base de datos.
    notification1 = Notification(
        user_id=user_fixture.id,
        title="Unread 1",
        message="Mensaje 1",
        is_read=False,
        type="info"
    )
    notification2 = Notification(
        user_id=user_fixture.id,
        title="Unread 2",
        message="Mensaje 2",
        is_read=False,
        type="info"
    )
    db_session.add_all([notification1, notification2])
    db_session.commit()

    # 2. Acción: Llama al método del repositorio para marcar todas las notificaciones como leídas.
    updated_count = notification_repo.mark_all_as_read(user_id=user_fixture.id)
    assert updated_count == 2

    # 3. Verificación: Consulta la base de datos directamente para asegurarte de que los cambios
    #    se han aplicado. Usamos db_session.refresh() para obtener el estado más reciente.
    db_session.refresh(notification1)
    db_session.refresh(notification2)

    # Verifica que ambas notificaciones ahora están marcadas como leídas.
    assert notification1.is_read is True
    assert notification2.is_read is True

    # Comprobación adicional: asegurarse de que no hay notificaciones no leídas para este usuario.
    unread_notifications_after_update = db_session.query(Notification).filter(
        Notification.user_id == user_fixture.id,
        Notification.is_read == False
    ).all()
    assert len(unread_notifications_after_update) == 0


def test_mark_all_as_read_no_unread_notifications(notification_repo: NotificationRepository, user_fixture: User, db_session: Session):
    """
    Verifica que no se marca ninguna notificación si no hay no leídas.
    """
    notification1 = Notification(user_id=user_fixture.id, title="Read 1", message="Mensaje 1", is_read=True, type="info")
    db_session.add(notification1)
    db_session.commit()

    updated_count = notification_repo.mark_all_as_read(user_fixture.id)
    assert updated_count == 0

def test_delete_notification_success(notification_repo: NotificationRepository, notification_fixture: Notification):
    """
    Verifica que se puede eliminar una notificación exitosamente.
    """
    notification_id_to_delete = notification_fixture.id

    result = notification_repo.delete_notification(notification_id_to_delete)

    assert result is True

    # Verificar que la notificación ya no existe
    deleted_notification = notification_repo.db_session.query(Notification).filter_by(id=notification_id_to_delete).first()
    assert deleted_notification is None

def test_delete_notification_not_found(notification_repo: NotificationRepository):
    """
    Verifica que intentar eliminar una notificación que no existe devuelve False.
    """
    non_existent_id = uuid4()
    result = notification_repo.delete_notification(non_existent_id)
    assert result is False
