"""API routes for company and analysis endpoints."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ..database import get_db
from ..schemas import (
    CompanyResponse, CompanyCreate, AnalysisResultResponse,
    ScreeningJobResponse, FavoriteCreate, FavoriteResponse, ScreeningRequest
)
from ..services.edgar_service import EdgarService
from ..services.company_service import CompanyService

router = APIRouter(prefix="/api/v1", tags=["companies"])


# ============== Company Endpoints ==============

@router.get("/companies", response_model=List[CompanyResponse])
async def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    sic_code: Optional[str] = None,
    ticker: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all companies with optional filtering."""
    service = CompanyService(db)
    return service.list_companies(skip=skip, limit=limit, sic_code=sic_code, ticker=ticker)


@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: UUID, db: Session = Depends(get_db)):
    """Get a specific company by ID."""
    service = CompanyService(db)
    company = service.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.post("/companies", response_model=CompanyResponse)
async def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    """Create a new company record."""
    service = CompanyService(db)
    return service.create_company(company)


@router.delete("/companies/{company_id}")
async def delete_company(company_id: UUID, db: Session = Depends(get_db)):
    """Delete a company and its analysis results."""
    service = CompanyService(db)
    success = service.delete_company(company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"message": "Company deleted successfully"}


# ============== Analysis Endpoints ==============

@router.get("/companies/{company_id}/analysis", response_model=List[AnalysisResultResponse])
async def get_company_analysis(company_id: UUID, db: Session = Depends(get_db)):
    """Get all analysis results for a company."""
    service = CompanyService(db)
    return service.get_company_analysis(company_id)


@router.get("/analysis", response_model=List[AnalysisResultResponse])
async def list_analysis_results(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    min_growth_ratio: Optional[float] = None,
    max_growth_ratio: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """List analysis results with optional filtering."""
    service = CompanyService(db)
    return service.list_analysis_results(
        skip=skip, limit=limit,
        min_growth_ratio=min_growth_ratio,
        max_growth_ratio=max_growth_ratio
    )


# ============== Screening Endpoints ==============

@router.post("/screen", response_model=ScreeningJobResponse)
async def start_screening(
    request: ScreeningRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start a new screening job."""
    service = CompanyService(db)
    job = service.create_screening_job(request.job_type, request.tickers)
    
    # Run screening in background
    background_tasks.add_task(
        run_screening_job,
        job_id=job.id,
        job_type=request.job_type,
        tickers=request.tickers,
        max_results=request.max_results
    )
    
    return job


@router.get("/screen/{job_id}", response_model=ScreeningJobResponse)
async def get_screening_status(job_id: UUID, db: Session = Depends(get_db)):
    """Get the status of a screening job."""
    service = CompanyService(db)
    job = service.get_screening_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Screening job not found")
    return job


@router.get("/screen", response_model=List[ScreeningJobResponse])
async def list_screening_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all screening jobs with optional status filter."""
    service = CompanyService(db)
    return service.list_screening_jobs(skip=skip, limit=limit, status=status)


# ============== Favorites Endpoints ==============

@router.get("/favorites", response_model=List[FavoriteResponse])
async def list_favorites(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List all favorite companies."""
    service = CompanyService(db)
    return service.list_favorites(skip=skip, limit=limit)


@router.post("/favorites", response_model=FavoriteResponse)
async def add_favorite(favorite: FavoriteCreate, db: Session = Depends(get_db)):
    """Add a company to favorites."""
    service = CompanyService(db)
    return service.add_favorite(favorite.company_id, favorite.notes)


@router.delete("/favorites/{favorite_id}")
async def remove_favorite(favorite_id: UUID, db: Session = Depends(get_db)):
    """Remove a company from favorites."""
    service = CompanyService(db)
    success = service.remove_favorite(favorite_id)
    if not success:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return {"message": "Favorite removed successfully"}


# ============== Health Check ==============

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "agent_puller"}


# Background task helper
def run_screening_job(job_id: UUID, job_type: str, tickers: Optional[List[str]], max_results: int):
    """Execute screening job in background."""
    from ..database import SessionLocal
    from ..services.edgar_service import EdgarService
    
    db = SessionLocal()
    try:
        edgar_service = EdgarService(db)
        edgar_service.run_screening(job_id, job_type, tickers, max_results)
    finally:
        db.close()
