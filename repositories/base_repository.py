from typing import TypeVar, Generic, Type, Union, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

# --- Importaciones corregidas basándonos en la estructura 'Core' ---
from Core.exceptions import IntegrityConstraintError
from Core.error_messages import GeneralErrors 
# -------------------------------------------------------------

ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType]):
    """
    Repositorio base que provee métodos CRUD genéricos.
    """

    def __init__(self, db: Session, model: Type[ModelType]):
        """
        Inicializa el repositorio.
        :param db: La sesión de la base de datos.
        :param model: El modelo de la tabla.
        """
        self.db = db
        self.model = model

    def create(self, entity_data: Union[dict, ModelType]) -> ModelType:
        """
        Crea una nueva entidad en la base de datos.
        :param entity_data: Un diccionario o una instancia del modelo.
        :return: La entidad creada.
        :raises IntegrityConstraintError: Si la entidad ya existe.
        """
        if isinstance(entity_data, dict):
            entity = self.model(**entity_data)
        else:
            entity = entity_data
        
        # Validar la existencia de la entidad para evitar duplicados
        existing_entity = self.get_by_unique_fields(entity)
        if existing_entity:
            raise IntegrityConstraintError(
                f"Ya existe una entidad de tipo {self.model.__name__} con los mismos campos únicos."
            )
        
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Obtiene una lista de todas las entidades con paginación.
        :param skip: Número de registros a omitir.
        :param limit: Número máximo de registros a retornar.
        :return: Una lista de entidades.
        """
        stmt = select(self.model).offset(skip).limit(limit)
        result = self.db.execute(stmt)
        return result.scalars().all()

    def get_by_id(self, entity_id: int) -> Union[ModelType, None]:
        """
        Obtiene una entidad por su ID.
        :param entity_id: El ID de la entidad.
        :return: La entidad, o None si no se encuentra.
        """
        stmt = select(self.model).where(self.model.id == entity_id)
        result = self.db.execute(stmt)
        return result.scalars().first()
    
    def get_by_unique_fields(self, entity: ModelType) -> Union[ModelType, None]:
        """
        Busca una entidad por sus campos únicos definidos en el modelo.
        """
        unique_fields = getattr(self.model, "unique_fields", [])
        if not unique_fields:
            return None

        clauses = []
        for field_name in unique_fields:
            value = getattr(entity, field_name)
            if value is not None:
                clauses.append(getattr(self.model, field_name) == value)
        
        if not clauses:
            return None
        
        stmt = select(self.model).where(and_(*clauses))
        return self.db.execute(stmt).scalars().first()

    def update(self, entity_id: int, update_data: dict) -> Union[ModelType, None]:
        """
        Actualiza una entidad existente por su ID.
        :param entity_id: El ID de la entidad.
        :param update_data: Un diccionario con los datos a actualizar.
        :return: La entidad actualizada, o None si no se encuentra.
        :raises IntegrityConstraintError: Si la actualización causa una colisión con campos únicos.
        """
        entity = self.get_by_id(entity_id)
        if not entity:
            return None
        
        # Validación de campos únicos si la actualización los afecta
        unique_fields = getattr(self.model, "unique_fields", [])
        if unique_fields:
            temp_entity_for_check = self.model(**entity.__dict__)
            for key, value in update_data.items():
                setattr(temp_entity_for_check, key, value)
            
            existing_entity = self.get_by_unique_fields(temp_entity_for_check)
            
            if existing_entity and existing_entity.id != entity_id:
                raise IntegrityConstraintError(
                    f"La actualización causaría una colisión con una entidad de tipo {self.model.__name__} existente."
                )

        for key, value in update_data.items():
            setattr(entity, key, value)
        
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity_id: int) -> bool:
        """
        Elimina una entidad por su ID.
        :param entity_id: El ID de la entidad.
        :return: True si la entidad fue eliminada, False si no se encontró.
        """
        entity = self.get_by_id(entity_id)
        if not entity:
            return False
        
        self.db.delete(entity)
        self.db.commit()
        return True
