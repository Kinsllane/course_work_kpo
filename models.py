from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class UserRole(str, enum.Enum):
    CLIENT = "client"
    TECHNICIAN = "technician"
    ADMIN = "admin"


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"
    REOPENED = "reopened"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password_hash = Column(String(100))
    full_name = Column(String(100))
    role = Column(Enum(UserRole))

    created_tickets = relationship(
        "Ticket",
        foreign_keys="[Ticket.client_id]",
        back_populates="client"
    )

    assigned_tickets = relationship(
        "Ticket",
        foreign_keys="[Ticket.technician_id]",
        back_populates="technician"
    )


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    description = Column(Text)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN)
    priority = Column(String(20))
    category = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    client_id = Column(Integer, ForeignKey("users.id"))
    technician_id = Column(Integer, ForeignKey("users.id"))

    client = relationship(
        "User",
        foreign_keys=[client_id],
        back_populates="created_tickets"
    )

    technician = relationship(
        "User",
        foreign_keys=[technician_id],
        back_populates="assigned_tickets"
    )


class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    changed_by = Column(Integer, ForeignKey("users.id"))
    field = Column(String(50))  # Поле (status, priority и т.д.)
    old_value = Column(String(100))
    new_value = Column(String(100))
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
