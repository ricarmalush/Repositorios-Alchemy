# En database/base.py
# from sqlalchemy.ext.declarative import declarative_base  # Forma antigua
from sqlalchemy.orm import declarative_base  # Forma nueva (recomendada)
Base = declarative_base()