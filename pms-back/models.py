from sqlalchemy import Column, Integer, String, DateTime, Enum, func, Float
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    real_name = Column(String(255))
    role = Column(Enum('admin', 'staff', 'teacher', 'student'), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now())

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    status = Column(Enum('normal', 'repair', 'scrapped'), nullable=False, default='正常')
    location = Column(String(255), nullable=False)
    purchase_date = Column(DateTime)
    description = Column(String(500))
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now())