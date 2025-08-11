# Core/exceptions.py

# Excepciones que son utilizadas para el manejo de errores

class ApplicationError(Exception):
    """Excepción base para errores de la aplicación."""
    def __init__(self, message: str, original_exception: Exception = None):
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception

# Excepciones generales para la capa del repositorio
class RepositoryError(ApplicationError):
    """Excepción base para errores en la capa del repositorio."""

    pass

class IntegrityConstraintError(RepositoryError):
    """Excepción para errores de integridad de la base de datos."""

    def __init__(self, message, original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception


class NotFoundError(RepositoryError):
    """Excepción para cuando una entidad no es encontrada."""
    def __init__(self, entity_name: str = "Entidad", entity_id: int = None, message: str = None):
        if message is None:
            if entity_id:
                message = f"{entity_name} con ID {entity_id} no encontrada."
            else:
                message = f"{entity_name} no encontrada."
        super().__init__(message)
        self.entity_name = entity_name
        self.entity_id = entity_id


class DuplicateNameError(RepositoryError):
    """Excepción para cuando se intenta crear una entidad con un nombre duplicado."""

    def __init__(self, name, entity_name):
        super().__init__(f"El nombre '{name}' ya existe para la entidad {entity_name}.")
        self.name = name
        self.entity_name = entity_name


class OperationFailedError(RepositoryError):
    """Excepción para cuando una operación del repositorio falla por razones desconocidas."""

    def __init__(self, entity_name, operation, original_exception=None):
        super().__init__(f"La operación de {operation} para la entidad {entity_name} falló.")
        self.entity_name = entity_name
        self.operation = operation
        self.original_exception = original_exception


# Excepciones específicas para la capa de servicios
class ServiceError(ApplicationError):
    """Excepción base para errores en la capa de servicios."""

    pass


class ValidationError(ServiceError):
    """Excepción para errores de validación de datos."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class EmptyValueError(ValidationError):
    """Excepción para cuando un campo obligatorio está vacío."""
    def __init__(self, field_name: str):
        super().__init__(f"El campo '{field_name}' no puede estar vacío.")


class InvalidUserTypeError(ServiceError):
    """Excepción para cuando un tipo de usuario no es válido."""

    pass


class InvalidWalkwayError(ServiceError):
    """Excepción para cuando una pasarela no es válida."""

    pass


class InvalidDayOfWeekError(ServiceError):
    """Excepción para cuando el día de la semana no es válido."""

    pass


class InvalidTimeFormatError(ServiceError):
    """Excepción para cuando el formato de la hora no es válido."""

    pass


class InvalidTimeRangeError(ServiceError):
    """Excepción para cuando el rango de tiempo no es válido."""

    pass

class ServiceError(ApplicationError):
    """Excepción base para errores en la capa de servicios."""
    pass

class PermissionError(ServiceError):
    """Excepción para errores de permisos o autorización."""
    pass
