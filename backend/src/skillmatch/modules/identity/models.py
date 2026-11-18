import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum
from skillmatch.core.database import Base

# 1. Definimos los roles posibles como un Enum (lista cerrada de opciones)
class UserRole(str, enum.Enum):
    TALENTO = "talento"
    EMPRESA = "empresa"
    ADMIN = "admin"

# 2. Definimos la tabla 'users'
class User(Base):
    __tablename__ = "users"

    # Columnas básicas de identidad
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False) # Aquí se guardará la contraseña cifrada
    role = Column(Enum(UserRole), nullable=False)  # Talento, Empresa o Admin
    status = Column(String, default="active")      # active, banned, pending...
    
    # Columnas de auditoría (cuándo se creó y cuándo entró por última vez)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)