from core.database.db import Base, engine
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    UUID,
    VARCHAR,
    LargeBinary,
    ForeignKey,
    JSON,
    Numeric,
)


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    """ organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organization.id"), nullable=True
    ) """
    username = Column(VARCHAR(200), unique=False)
    email = Column(VARCHAR(200), unique=False)
    address = Column(VARCHAR(200), nullable=False)
    phone_number = Column(VARCHAR(200), unique=False)
    password = Column(
        LargeBinary,
        nullable=False,
    )
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    type_user = Column(VARCHAR(200), default="user", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)

    user_organization = relationship("UserOrganization", back_populates="users")
    verification_code = relationship("VerificationCode", back_populates="user")


class Organization(Base):
    __tablename__ = "organization"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(VARCHAR(200), unique=True)
    email = Column(VARCHAR(200), unique=True)
    phone_number = Column(VARCHAR(200), unique=True)

    province = Column(VARCHAR(200), nullable=True)
    city = Column(VARCHAR(200), nullable=True)
    type_organization = Column(VARCHAR(200), nullable=True)
    address = Column(VARCHAR(200), nullable=True)
    status = Column(Boolean, default=True)
    logo = Column(VARCHAR(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    website = Column(VARCHAR(200), nullable=False)

    admin = relationship(
        "User",
        primaryjoin="Organization.admin_id == User.id",
        uselist=False,
    )
    user_organization = relationship("UserOrganization", back_populates="organization")
    verification_code = relationship("VerificationCode", back_populates="organization")
    subscriptions = relationship("Subscription", back_populates="organization")
    services = relationship("Services", back_populates="organization")
    counter = relationship("Counter", back_populates="organization")
    ticket = relationship("Ticket", back_populates="organization")


class UserOrganization(Base):
    __tablename__ = "user_organization"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organization.id"), nullable=True
    )

    users = relationship("User", back_populates="user_organization")
    organization = relationship("Organization", back_populates="user_organization")


class VerificationCode(Base):
    __tablename__ = "verification_code"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    code = Column(VARCHAR(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="verification_code")
    user = relationship("User", back_populates="verification_code")


class Plan(Base):
    __tablename__ = "plans"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(VARCHAR(200), unique=True, nullable=False)
    price = Column(Numeric(10, 2), default=0.0)
    duration_days = Column(Integer, default=30)  # 30 for monthly, 365 for annual
    restrictions = Column(
        JSON, nullable=True
    )  # e.g., {"max_users": 5, "max_queries": 100}
    created_at = Column(DateTime, default=datetime.utcnow)

    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False
    )
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)
    start_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")


class Services(Base):
    __tablename__ = "services"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organizatio_id = Column(
        UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False
    )
    # organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    name = Column(VARCHAR(200), unique=True, nullable=False)
    restrictions = Column(
        JSON, nullable=True
    )  # e.g., {"max_users": 5, "max_queries": 100}
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="services")
    service_counters = relationship("ServiceCounter", back_populates="service")
    service_tickets = relationship("ServiceTicket", back_populates="service")
    counter = relationship("Counter", back_populates="services")


class Counter(Base):
    __tablename__ = "counter"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # service_id removed to use many-to-many relationship
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False)
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False
    )
    name = Column(VARCHAR(200), unique=True, nullable=False)
    count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="counter")
    ticket = relationship("Ticket", back_populates="counter")
    service_counters = relationship("ServiceCounter", back_populates="counter")
    services = relationship("Services", back_populates="counter")


class Ticket(Base):
    __tablename__ = "ticket"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    counter_id = Column(UUID(as_uuid=True), ForeignKey("counter.id"), nullable=False)
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False
    )
    # service_id removed to use many-to-many relationship
    name = Column(VARCHAR(200), unique=True, nullable=False)
    count = Column(Integer, default=0)
    status = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    counter = relationship("Counter", back_populates="ticket")
    organization = relationship("Organization", back_populates="ticket")
    service_tickets = relationship("ServiceTicket", back_populates="ticket")


class ServiceCounter(Base):
    __tablename__ = "service_counter"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False)
    counter_id = Column(UUID(as_uuid=True), ForeignKey("counter.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    service = relationship("Services", back_populates="service_counters")
    counter = relationship("Counter", back_populates="service_counters")


class ServiceTicket(Base):
    __tablename__ = "service_ticket"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("ticket.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    service = relationship("Services", back_populates="service_tickets")
    ticket = relationship("Ticket", back_populates="service_tickets")


def start_tables():
    Base.metadata.create_all(bind=engine)
