"""Company and analysis-related SQLAlchemy models."""
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Date, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..database import Base


class Company(Base):
    """SEC registered company model."""
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cik = Column(String(20), unique=True, nullable=False, index=True)
    ticker = Column(String(10), index=True)
    company_name = Column(String(500), nullable=False)
    sic_code = Column(String(10), index=True)
    sic_description = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    analysis_results = relationship("AnalysisResult", back_populates="company", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Company(ticker={self.ticker}, name={self.company_name})>"


class AnalysisResult(Base):
    """Narrative shift analysis result for a company."""
    __tablename__ = "analysis_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    # Segment analysis metrics
    legacy_growth_rate = Column(Numeric(10, 4))
    new_segment_growth_rate = Column(Numeric(10, 4))
    growth_ratio = Column(Numeric(10, 4))
    new_segment_revenue_pct = Column(Numeric(10, 4))
    
    # Detailed segment data
    segments_data = Column(JSONB)
    
    # Metadata
    analysis_date = Column(Date, nullable=False)
    fiscal_year = Column(Integer)
    form_type = Column(String(20))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="analysis_results")
    
    def __repr__(self):
        return f"<AnalysisResult(company_id={self.company_id}, growth_ratio={self.growth_ratio})>"


class ScreeningJob(Base):
    """Background job for screening operations."""
    __tablename__ = "screening_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_type = Column(String(50), nullable=False)
    status = Column(String(20), default="pending")
    total_companies = Column(Integer, default=0)
    processed_companies = Column(Integer, default=0)
    results_count = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ScreeningJob(id={self.id}, status={self.status})>"


class Favorite(Base):
    """User favorite companies."""
    __tablename__ = "favorites"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), unique=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="favorites")
    
    def __repr__(self):
        return f"<Favorite(company_id={self.company_id})>"
