from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
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

    # Явно указываем foreign keys для отношений
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

    comments = relationship("Comment", back_populates="user")


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

    comments = relationship("Comment", back_populates="ticket")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    ticket = relationship("Ticket", back_populates="comments")
    user = relationship("User", back_populates="comments")