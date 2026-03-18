from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Float, Enum, func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class ServiceCategory(str, enum.Enum):
    HAIR = "hair"
    NAILS = "nails"
    MAKEUP = "makeup"
    FACIAL = "facial"
    SPA = "spa"

class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="refresh_tokens")

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    category = Column(Enum(ServiceCategory), nullable=False)
    price = Column(Float, nullable=False)
    duration_minutes = Column(Integer, default=60, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    bookings = relationship("Booking", back_populates="service")


class Master(Base):
    __tablename__ = "masters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    specialty = Column(String)
    description = Column(String)
    photo_url = Column(String)
    is_active = Column(Boolean, default=True)
    rating = Column(Float, default=5.0)
    created_at = Column(DateTime, default = func.now())

    bookings = relationship("Booking", back_populates="master")
    portfolio_items = relationship("PortfolioItem", back_populates="master")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    master_id = Column(Integer, ForeignKey("masters.id"), nullable=False)

    client_name = Column(String, nullable=False)
    client_phone = Column(String, nullable=False)
    client_email = Column(String, nullable=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    client_comment = Column(Text)

    user = relationship("User", back_populates="bookings")
    service = relationship("Service", back_populates="bookings")
    master = relationship("Master", back_populates="bookings")


class PortfolioItem(Base):
    __tablename__ = "portfolio_items"

    id = Column(Integer, primary_key=True, index=True)
    master_id = Column(Integer, ForeignKey("masters.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(Enum(ServiceCategory), nullable=False)
    image_url = Column(String, nullable=False)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    master = relationship("Master", back_populates="portfolio_items")


class ContactInfo(Base):
    __tablename__ = "contact_info"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String)
    phone = Column(String)
    email = Column(String)
    working_hours = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    social_telegram = Column(String)
    social_instagram = Column(String)
    social_vk = Column(String)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


