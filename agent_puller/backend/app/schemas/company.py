"""Pydantic schemas for company-related data."""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import date, datetime
from uuid import UUID


# ============== Company Schemas ==============

class CompanyBase(BaseModel):
    """Base company schema with common fields."""
    cik: str = Field(..., min_length=10, max_length=10)
    ticker: Optional[str] = Field(None, max_length=10)
    company_name: str = Field(..., max_length=500)
    sic_code: Optional[str] = Field(None, max_length=10)
    sic_description: Optional[str] = Field(None, max_length=500)


class CompanyCreate(CompanyBase):
    """Schema for creating a new company."""
    pass


class CompanyUpdate(BaseModel):
    """Schema for updating company information."""
    ticker: Optional[str] = None
    company_name: Optional[str] = None
    sic_description: Optional[str] = None


class SegmentData(BaseModel):
    """Individual segment data."""
    name: str
    revenue: float
    account: Optional[str] = None


class CompanyResponse(CompanyBase):
    """Schema for company response."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CompanyWithAnalysis(CompanyResponse):
    """Company response with latest analysis."""
    latest_analysis: Optional["AnalysisResultResponse"] = None


# ============== Analysis Result Schemas ==============

class AnalysisResultBase(BaseModel):
    """Base analysis result schema."""
    legacy_growth_rate: Optional[float] = None
    new_segment_growth_rate: Optional[float] = None
    growth_ratio: Optional[float] = None
    new_segment_revenue_pct: Optional[float] = None


class AnalysisResultCreate(AnalysisResultBase):
    """Schema for creating an analysis result."""
    company_id: UUID
    analysis_date: date
    fiscal_year: Optional[int] = None
    form_type: Optional[str] = None
    segments_data: Optional[List[SegmentData]] = None


class AnalysisResultResponse(AnalysisResultBase):
    """Schema for analysis result response."""
    id: UUID
    company_id: UUID
    analysis_date: date
    fiscal_year: Optional[int] = None
    form_type: Optional[str] = None
    segments_data: Optional[List[SegmentData]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== Screening Job Schemas ==============

class ScreeningJobResponse(BaseModel):
    """Schema for screening job response."""
    id: UUID
    job_type: str
    status: str
    total_companies: int
    processed_companies: int
    results_count: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScreeningRequest(BaseModel):
    """Request schema for starting a screening job."""
    job_type: str = Field(default="narrative_shift", pattern="^(narrative_shift|specific_tickers)$")
    tickers: Optional[List[str]] = None
    max_results: int = Field(default=100, ge=1, le=500)


# ============== Favorite Schemas ==============

class FavoriteCreate(BaseModel):
    """Schema for creating a favorite."""
    company_id: UUID
    notes: Optional[str] = None


class FavoriteResponse(BaseModel):
    """Schema for favorite response."""
    id: UUID
    company_id: UUID
    notes: Optional[str] = None
    created_at: datetime
    company: Optional[CompanyResponse] = None
    
    class Config:
        from_attributes = True


# Update forward references
CompanyWithAnalysis.model_rebuild()
