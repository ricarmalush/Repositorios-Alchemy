# backend/SQLALCHEMY_REGADIO/core/error_messages.py

class BaseEntityErrors:
    """Clase base con las plantillas de los mensajes de error comunes."""
    # Las plantillas deben mantener sus placeholders para el formateo en tiempo de ejecución
    NAME_EMPTY_TEMPLATE = "El nombre del {entity_name} no puede estar vacío."
    NAME_DUPLICATE_TEMPLATE = "Ya existe un {entity_name} con el nombre '{name}'."
    NOT_FOUND_TEMPLATE = "{entity_name} con ID {{{id_field}}} no encontrado."


class UserTypeErrors(BaseEntityErrors):
    """Mensajes de error para la entidad UserType."""
    ENTITY_NAME = "tipo de usuario"
    
    # Formatea los mensajes que solo requieren el nombre de la entidad.
    # Los que requieren datos dinámicos (como {name}) se dejan como plantillas.
    NAME_EMPTY = BaseEntityErrors.NAME_EMPTY_TEMPLATE.format(entity_name=ENTITY_NAME)
    NAME_DUPLICATE = "Ya existe un tipo de usuario con el nombre '{name}'."
    NOT_FOUND = "tipo de usuario con ID {user_type_id} no encontrado."
    
    # Mensajes específicos de esta entidad
    HAS_ASSOCIATED_USERS = "No se puede eliminar el tipo de usuario con ID {user_type_id} porque tiene usuarios asociados."


class WalkwayErrors(BaseEntityErrors):
    """Mensajes de error para la entidad Walkway."""
    ENTITY_NAME = "andador"

    NAME_EMPTY = BaseEntityErrors.NAME_EMPTY_TEMPLATE.format(entity_name=ENTITY_NAME)
    NAME_DUPLICATE = "Ya existe un andador con el nombre '{name}'."
    NOT_FOUND = "andador con ID {walkway_id} no encontrado."


class AccessScheduleRuleErrors:
    """Mensajes de error relacionados con el modelo AccessScheduleRule."""
    INVALID_DAY_OF_WEEK = "El día de la semana no es válido. Debe ser un número entre 0 (lunes) y 6 (domingo)."
    INVALID_TIME_RANGE = "La hora de inicio ({start_time}) no puede ser posterior o igual a la hora de fin ({end_time})."
    USER_TYPE_NOT_FOUND = "No se puede crear la regla. El tipo de usuario con ID {user_type_id} no existe."
    RULE_NOT_FOUND = "Regla de acceso con ID {rule_id} no encontrada."


class UserErrors(BaseEntityErrors):
    """Mensajes de error para la entidad User."""
    ENTITY_NAME = "usuario"

    NAME_EMPTY = BaseEntityErrors.NAME_EMPTY_TEMPLATE.format(entity_name=ENTITY_NAME)
    NAME_DUPLICATE = "Ya existe un usuario con el nombre '{name}'."
    NOT_FOUND = "usuario con ID {user_id} no encontrado."

    USERNAME_DUPLICATE = "Ya existe un usuario con el nombre de usuario '{username}'. Por favor, elija uno diferente."
    EMAIL_DUPLICATE = "Ya existe un usuario con el email '{email}'. Por favor, elija uno diferente."
    ADMIN_SELF_DELETE = "Un administrador no puede eliminarse a sí mismo."
    ADMIN_SELF_DEMOTE = "Un administrador no puede degradar su propio rol."
    NO_PERMISSION = "No tienes permiso para {action} este usuario."

class UserWateringScheduleErrors(BaseEntityErrors):
    """Mensajes de error para la entidad UserWateringSchedule."""
    ENTITY_NAME = "programación de riego"
    
    NOT_FOUND = BaseEntityErrors.NOT_FOUND_TEMPLATE.format(entity_name=ENTITY_NAME, id_field="schedule_id")
    MAX_DURATION_EXCEEDED = "La duración máxima permitida de riego es de {max_duration_minutes} minutos."
    OVERLAPPING_SCHEDULE = "La nueva programación se superpone con una programación existente del usuario."
    SCHEDULE_RULE_MISMATCH = "El horario propuesto no cumple con las reglas de acceso del tipo de usuario para ese día."
    UPDATE_OVERLAPPING_SCHEDULE = "La programación actualizada se superpone con una programación existente del usuario."
    UPDATE_SCHEDULE_RULE_MISMATCH = "El horario actualizado no cumple con las reglas de acceso del tipo de usuario para ese día."


class GeneralErrors:
    """Mensajes de error de uso general."""
    UNEXPECTED_ERROR = "Ocurrió un error inesperado al {operation} el {entity_name}. Detalle: {detail}"
