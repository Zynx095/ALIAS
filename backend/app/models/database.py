"""ALIAS Database Foundation.

SQLAlchemy models and database session management.
Default: SQLite for local development.
"""
import os
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, Boolean,
    ForeignKey, JSON, create_engine
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from core.config import get_settings

settings = get_settings()

# Database engine — SQLite by default
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


# ============================================================
# ALIAS Core Models
# ============================================================

class LoginEvent(Base):
    """Records a single login/authentication event for analysis."""
    __tablename__ = "login_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)  # IPv4/IPv6
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location = Column(String(255), nullable=True)  # City, Country
    device_fingerprint = Column(String(255), nullable=True)
    user_agent = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    auth_status = Column(String(20), nullable=False, default="SUCCESS")  # SUCCESS, FAILURE
    failed_attempts = Column(Integer, nullable=False, default=0)
    access_pattern = Column(String(255), nullable=True)  # e.g., "VPN", "DIRECT", "TOR"
    event_hash = Column(String(64), unique=True, index=True, nullable=True)
    processing_status = Column(String(20), nullable=False, default="INGESTED")  # INGESTED, ANALYZING, COMPLETE
    enriched_data = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    anomalies = relationship("AnomalyRecord", back_populates="event", cascade="all, delete-orphan")
    risk_assessment = relationship("RiskAssessment", back_populates="event", uselist=False, cascade="all, delete-orphan")
    investigation = relationship("InvestigationReport", back_populates="event", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<LoginEvent(id={self.id}, user={self.user_id}, ip={self.ip_address}, status={self.auth_status})>"


class UserBaseline(Base):
    """Stores a user's historical behavioral baseline for comparison."""
    __tablename__ = "user_baselines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, unique=True, index=True)
    known_devices = Column(JSON, nullable=True, default=list)  # List of device fingerprints
    known_ips = Column(JSON, nullable=True, default=list)  # List of known IPs
    known_locations = Column(JSON, nullable=True, default=list)  # List of {city, country, lat, lon}
    typical_hours = Column(JSON, nullable=True, default=dict)  # {start: int, end: int, timezone: str}
    auth_profile = Column(JSON, nullable=True, default=dict)  # Authentication outcome behavior
    access_patterns = Column(JSON, nullable=True, default=dict)  # Network/routing access patterns
    last_login_ip = Column(String(45), nullable=True)
    last_login_lat = Column(Float, nullable=True)
    last_login_lon = Column(Float, nullable=True)
    last_login_timestamp = Column(DateTime, nullable=True)
    last_login_device = Column(String(255), nullable=True)
    login_count = Column(Integer, nullable=False, default=0)
    version = Column(String(64), nullable=True)  # bsl_xxxxx
    status = Column(String(50), nullable=False, default="NO_BASELINE")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserBaseline(user={self.user_id}, status={self.status}, version={self.version}, logins={self.login_count})>"


class AnomalyRecord(Base):
    """Records a detected anomaly for a specific login event."""
    __tablename__ = "anomaly_records"

    id = Column(Integer, primary_key=True, index=True)
    anomaly_id = Column(String(64), nullable=False, unique=True, index=True)
    event_id = Column(Integer, ForeignKey("login_events.id"), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    anomaly_type = Column(String(50), nullable=False)
    detector = Column(String(50), nullable=False)
    signal = Column(String(50), nullable=False)
    feature = Column(String(100), nullable=False)
    observed_value = Column(String(255), nullable=True)
    expected_state = Column(String(255), nullable=True)
    evidence = Column(JSON, nullable=True, default=dict)
    explanation = Column(Text, nullable=True)
    baseline_version = Column(String(64), nullable=True)
    rule_id = Column(String(50), nullable=True)
    detected_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    event = relationship("LoginEvent", back_populates="anomalies")

    def __repr__(self):
        return f"<AnomalyRecord(anomaly_id={self.anomaly_id}, type={self.anomaly_type}, detector={self.detector})>"


class RiskAssessment(Base):
    """Persisted deterministic multi-signal risk assessment for an event."""
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(String(64), nullable=False, unique=True, index=True)
    event_id = Column(Integer, ForeignKey("login_events.id"), nullable=False, unique=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    risk_score = Column(Float, nullable=False, default=0.0)
    severity = Column(String(20), nullable=False, default="LOW")
    risk_factors = Column(JSON, nullable=True, default=list)
    correlation_factors = Column(JSON, nullable=True, default=list)
    correlated_anomalies = Column(JSON, nullable=True, default=list)
    explanation = Column(Text, nullable=True)
    scoring_version = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    event = relationship("LoginEvent", back_populates="risk_assessment")

    def __repr__(self):
        return f"<RiskAssessment(risk_id={self.risk_id}, score={self.risk_score}, severity={self.severity})>"


class InvestigationReport(Base):
    """AI-generated investigation report for a suspicious login event."""
    __tablename__ = "investigation_reports"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(String(64), nullable=False, unique=True, index=True)
    event_id = Column(Integer, ForeignKey("login_events.id"), nullable=False, unique=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    risk_score = Column(Float, nullable=False, default=0.0)
    severity = Column(String(20), nullable=False, default="LOW")
    summary = Column(Text, nullable=True)
    indicators = Column(JSON, nullable=True, default=list)
    attack_scenario = Column(Text, nullable=True)
    recommendations = Column(JSON, nullable=True, default=list)
    observed_evidence = Column(JSON, nullable=True, default=dict)
    correlated_factors = Column(JSON, nullable=True, default=list)
    supporting_anomaly_ids = Column(JSON, nullable=True, default=list)
    llm_provider = Column(String(50), nullable=True)
    llm_model = Column(String(50), nullable=True)
    investigation_version = Column(String(50), nullable=False, default="investigation_v1")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    event = relationship("LoginEvent", back_populates="investigation")

    def __repr__(self):
        return f"<InvestigationReport(investigation_id={self.investigation_id}, risk={self.risk_score}, severity={self.severity})>"


# ============================================================
# Legacy Models (Preserved from ShadowGuard for compatibility)
# ============================================================

class ProxyEvent(Base):
    """Legacy: ShadowGuard proxy event log. Preserved for backward compatibility."""
    __tablename__ = "proxy_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    employee_id = Column(String, index=True)
    prompt_text = Column(String)
    risk_score = Column(Float)
    action_taken = Column(String)


class VideoAnalysis(Base):
    """Legacy: ShadowGuard video deepfake analysis. Preserved for backward compatibility."""
    __tablename__ = "video_analysis"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    deepfake_score = Column(Float)
    status = Column(String)


class AudioAnalysis(Base):
    """Legacy: ShadowGuard audio analysis. Preserved for backward compatibility."""
    __tablename__ = "audio_analysis"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    deepfake_score = Column(Float)
    spectral_entropy = Column(Float)
    status = Column(String)
