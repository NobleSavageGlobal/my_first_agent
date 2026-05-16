"""Company-related business logic service."""
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from ..models import Company, AnalysisResult, ScreeningJob, Favorite
from ..schemas import CompanyCreate, CompanyResponse, AnalysisResultResponse


class CompanyService:
    """Service for company-related operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def list_companies(
        self,
        skip: int = 0,
        limit: int = 100,
        sic_code: Optional[str] = None,
        ticker: Optional[str] = None
    ) -> List[Company]:
        """List companies with optional filtering."""
        query = self.db.query(Company)
        
        if sic_code:
            query = query.filter(Company.sic_code == sic_code)
        if ticker:
            query = query.filter(Company.ticker == ticker.upper())
        
        return query.offset(skip).limit(limit).all()
    
    def get_company(self, company_id: UUID) -> Optional[Company]:
        """Get a company by ID."""
        return self.db.query(Company).filter(Company.id == company_id).first()
    
    def create_company(self, company_data: CompanyCreate) -> Company:
        """Create a new company record."""
        company = Company(
            cik=company_data.cik,
            ticker=company_data.ticker,
            company_name=company_data.company_name,
            sic_code=company_data.sic_code,
            sic_description=company_data.sic_description
        )
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company
    
    def delete_company(self, company_id: UUID) -> bool:
        """Delete a company and its related data."""
        company = self.get_company(company_id)
        if not company:
            return False
        self.db.delete(company)
        self.db.commit()
        return True
    
    def get_company_analysis(self, company_id: UUID) -> List[AnalysisResult]:
        """Get all analysis results for a company."""
        return (
            self.db.query(AnalysisResult)
            .filter(AnalysisResult.company_id == company_id)
            .order_by(AnalysisResult.analysis_date.desc())
            .all()
        )
    
    def list_analysis_results(
        self,
        skip: int = 0,
        limit: int = 100,
        min_growth_ratio: Optional[float] = None,
        max_growth_ratio: Optional[float] = None
    ) -> List[AnalysisResult]:
        """List analysis results with optional filtering."""
        query = self.db.query(AnalysisResult)
        
        if min_growth_ratio is not None:
            query = query.filter(AnalysisResult.growth_ratio >= min_growth_ratio)
        if max_growth_ratio is not None:
            query = query.filter(AnalysisResult.growth_ratio <= max_growth_ratio)
        
        return query.offset(skip).limit(limit).all()
    
    # ============== Screening Job Methods ==============
    
    def create_screening_job(
        self,
        job_type: str,
        tickers: Optional[List[str]] = None
    ) -> ScreeningJob:
        """Create a new screening job."""
        job = ScreeningJob(
            job_type=job_type,
            status="pending"
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def get_screening_job(self, job_id: UUID) -> Optional[ScreeningJob]:
        """Get a screening job by ID."""
        return self.db.query(ScreeningJob).filter(ScreeningJob.id == job_id).first()
    
    def list_screening_jobs(
        self,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None
    ) -> List[ScreeningJob]:
        """List screening jobs with optional status filter."""
        query = self.db.query(ScreeningJob)
        
        if status:
            query = query.filter(ScreeningJob.status == status)
        
        return (
            query
            .order_by(ScreeningJob.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def update_screening_job(
        self,
        job_id: UUID,
        status: Optional[str] = None,
        total_companies: Optional[int] = None,
        processed_companies: Optional[int] = None,
        results_count: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> Optional[ScreeningJob]:
        """Update screening job progress."""
        job = self.get_screening_job(job_id)
        if not job:
            return None
        
        if status:
            job.status = status
        if total_companies is not None:
            job.total_companies = total_companies
        if processed_companies is not None:
            job.processed_companies = processed_companies
        if results_count is not None:
            job.results_count = results_count
        if error_message:
            job.error_message = error_message
        
        if status == "running" and not job.started_at:
            job.started_at = datetime.utcnow()
        elif status in ("completed", "failed"):
            job.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(job)
        return job
    
    # ============== Favorite Methods ==============
    
    def list_favorites(self, skip: int = 0, limit: int = 100) -> List[Favorite]:
        """List all favorite companies."""
        return (
            self.db.query(Favorite)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def add_favorite(self, company_id: UUID, notes: Optional[str] = None) -> Favorite:
        """Add a company to favorites."""
        # Check if company exists
        company = self.get_company(company_id)
        if not company:
            raise ValueError("Company not found")
        
        # Check if already favorited
        existing = (
            self.db.query(Favorite)
            .filter(Favorite.company_id == company_id)
            .first()
        )
        if existing:
            return existing
        
        favorite = Favorite(company_id=company_id, notes=notes)
        self.db.add(favorite)
        self.db.commit()
        self.db.refresh(favorite)
        return favorite
    
    def remove_favorite(self, favorite_id: UUID) -> bool:
        """Remove a company from favorites."""
        favorite = self.db.query(Favorite).filter(Favorite.id == favorite_id).first()
        if not favorite:
            return False
        self.db.delete(favorite)
        self.db.commit()
        return True
