"""SQLAlchemy ORM models for MediFlow AI CRM."""

from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, Date,
    ForeignKey, JSON, Enum as SAEnum
)
from sqlalchemy.orm import DeclarativeBase, relationship
import enum


class Base(DeclarativeBase):
    pass


# ── Enums ──

class UserRole(str, enum.Enum):
    REP = "rep"
    MANAGER = "manager"


class InteractionType(str, enum.Enum):
    IN_PERSON = "in-person"
    VIRTUAL = "virtual"
    PHONE = "phone"
    EMAIL = "email"


class Sentiment(str, enum.Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class HCPTier(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"


class FollowUpStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class Priority(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ── Models ──

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.REP, nullable=False)
    territory = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    interactions = relationship("Interaction", back_populates="user")
    follow_ups = relationship("FollowUp", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class HCP(Base):
    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    specialty = Column(String(255), nullable=False)
    institution = Column(String(255), nullable=False)
    city = Column(String(255), nullable=True)
    state = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    npi_number = Column(String(20), nullable=True, unique=True)
    tier = Column(SAEnum(HCPTier), default=HCPTier.B, nullable=False)
    preferred_contact_method = Column(String(50), default="in-person")
    relationship_score = Column(Float, default=50.0, nullable=False)
    engagement_data = Column(JSON, default=dict, nullable=False)
    # engagement_data schema:
    # {
    #   "visit_count": 7,
    #   "avg_sentiment": 0.85,
    #   "follow_up_completion_rate": 0.9,
    #   "last_product_discussed": "Cardiolex",
    #   "typical_objections": ["side effects", "cost"],
    #   "buying_interest": "high",
    #   "engagement_trend": "growing"
    # }
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    interactions = relationship("Interaction", back_populates="hcp")
    follow_ups = relationship("FollowUp", back_populates="hcp")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    interaction_date = Column(Date, default=date.today, nullable=False)
    interaction_type = Column(SAEnum(InteractionType), default=InteractionType.IN_PERSON, nullable=False)
    products_discussed = Column(JSON, default=list, nullable=False)
    key_topics = Column(Text, nullable=True)
    sentiment = Column(SAEnum(Sentiment), default=Sentiment.NEUTRAL, nullable=False)
    sentiment_score = Column(Float, default=0.5, nullable=False)
    follow_up_date = Column(Date, nullable=True)
    follow_up_actions = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    ai_executive_summary = Column(JSON, nullable=True)
    # ai_executive_summary schema:
    # {
    #   "key_outcomes": ["..."],
    #   "next_actions": ["..."],
    #   "risks": ["..."]
    # }
    ai_confidence = Column(Float, nullable=True)
    entities_extracted = Column(JSON, nullable=True)
    # entities_extracted schema:
    # {
    #   "doctor": {"value": "Dr. Sarah Chen", "confidence": 0.98},
    #   "product": {"value": "Cardiolex", "confidence": 0.96},
    #   "sentiment": {"value": "positive", "confidence": 0.91},
    #   "follow_up": {"value": "2025-07-20", "confidence": 0.95}
    # }
    compliance_flags = Column(JSON, nullable=True)
    strategic_insight = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    samples_dropped = Column(JSON, default=list, nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    hcp = relationship("HCP", back_populates="interactions")
    user = relationship("User", back_populates="interactions")
    follow_ups = relationship("FollowUp", back_populates="interaction")


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"), nullable=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    due_date = Column(Date, nullable=False)
    action_description = Column(Text, nullable=False)
    ai_suggested_actions = Column(JSON, default=list, nullable=False)
    # e.g. ["Share clinical trial data", "Arrange product demo", "Deliver samples"]
    status = Column(SAEnum(FollowUpStatus), default=FollowUpStatus.PENDING, nullable=False)
    priority = Column(SAEnum(Priority), default=Priority.MEDIUM, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    interaction = relationship("Interaction", back_populates="follow_ups")
    hcp = relationship("HCP", back_populates="follow_ups")
    user = relationship("User", back_populates="follow_ups")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(50), nullable=False)  # "create", "update", "delete"
    entity_type = Column(String(50), nullable=False)  # "interaction", "follow_up"
    entity_id = Column(Integer, nullable=False)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="audit_logs")
