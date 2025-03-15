from sqlalchemy import Column, Integer, String, DateTime, Enum, func, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

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

class Repair(Base):
    __tablename__ = "repairs"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum('equipment', 'facility'), nullable=False)
    asset_id = Column(String(20))
    location = Column(String(100), nullable=False)
    description = Column(String, nullable=False)
    submitter_id = Column(Integer, nullable=False)
    status = Column(Enum('pending', 'processing', 'completed', 'cancelled'), nullable=False, default='pending')
    submit_time = Column(DateTime, default=func.now())
    complete_time = Column(DateTime)


class Notice(Base):
    __tablename__ = 'notices'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    publisher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    publish_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='published')

    publisher = relationship("User", back_populates="notices")

User.notices = relationship("Notice", back_populates="publisher", cascade="all, delete-orphan")


class Finance(Base):
    __tablename__ = "finances"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum('repair', 'purchase', 'maintenance', 'other'), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(500))
    operator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    create_time = Column(DateTime, default=func.now())


class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    room_no = Column(String(50), unique=True, nullable=False)
    building = Column(String(50), nullable=False)
    type = Column(Enum('multimedia', 'normal'), nullable=False)
    capacity = Column(Integer, nullable=False)
    facilities = Column(Text)
    status = Column(Enum('available', 'maintenance', 'booked'), nullable=False, default='available')

class ClassroomBooking(Base):
    __tablename__ = "classroom_bookings"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey('classrooms.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    purpose = Column(String(500), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(Enum('pending', 'approved', 'rejected'), nullable=False, default='pending')
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now())

    classroom = relationship("Classroom")
    user = relationship("User")