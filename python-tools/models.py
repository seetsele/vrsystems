from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    JSON,
    func,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Run(Base):
    __tablename__ = "runs"
    id = Column(String(64), primary_key=True)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    cmd = Column(Text)
    exit_code = Column(Integer)
    stdout = Column(Text)
    parsed = Column(JSON)


class Webhook(Base):
    __tablename__ = "webhooks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text, nullable=False)
    enabled = Column(Boolean, default=True)


class Provider(Base):
    __tablename__ = "providers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False, unique=True)
    encrypted_secret = Column(Text)


class WebhookQueue(Base):
    __tablename__ = "webhook_queue"
    id = Column(Integer, primary_key=True, autoincrement=True)
    webhook_id = Column(Integer)
    run_id = Column(String(64))
    attempts = Column(Integer, default=0)
    next_try = Column(DateTime)


class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    webhook_id = Column(Integer)
    run_id = Column(String(64))
    status_code = Column(Integer)
    response = Column(Text)
    timestamp = Column(DateTime, server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(String(64), primary_key=True)
    ts = Column(DateTime, server_default=func.now())
    actor = Column(String(128))
    action = Column(String(256))
    details = Column(Text)
