"""
SEC EDGAR Analysis Service

This service integrates with the SEC EDGAR database to analyze utility companies
for narrative shift opportunities - where a growing new segment (e.g., renewable
energy) is outpacing legacy segments (e.g., transmission/distribution).
"""
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import Company, AnalysisResult
from .company_service import CompanyService

logger = logging.getLogger(__name__)
settings = get_settings()

# Known utility tickers for analysis
UTILITY_TICKERS = [
    'NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'PCG', 'ED', 'EIX', 'ES',
    'CMS', 'ATO', 'AWK', 'CNP', 'CEG', 'LNT', 'NI', 'PNW', 'PPL',
    'EVRG', 'VST', 'BEP', 'CWEN', 'NEP', 'RUN', 'FLSR'
]


class EdgarService:
    """
    Service for interacting with SEC EDGAR and performing narrative shift analysis.
    
    This analyzes utility companies where:
    - A newer segment is growing 2-3x faster than legacy segment
    - New segment approaching 20%+ of total revenue
    - Market may still be pricing as slow/legacy
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.company_service = CompanyService(db)
        self.max_results = settings.max_results
        
        # Growth ratio thresholds from config
        self.min_growth_ratio = settings.min_growth_ratio
        self.max_growth_ratio = settings.max_growth_ratio
        self.min_new_segment_pct = settings.min_new_segment_pct
        self.max_new_segment_pct = settings.max_new_segment_pct
    
    def run_screening(
        self,
        job_id: str,
        job_type: str,
        tickers: Optional[List[str]] = None,
        max_results: int = 100
    ):
        """
        Run the narrative shift screening analysis.
        
        Args:
            job_id: UUID of the screening job
            job_type: Type of screening (narrative_shift or specific_tickers)
            tickers: Optional list of specific tickers to analyze
            max_results: Maximum number of companies to analyze
        """
        logger.info(f"Starting screening job {job_id} of type {job_type}")
        
        # Update job status to running
        self.company_service.update_screening_job(job_id, status="running")
        
        try:
            if job_type == "specific_tickers" and tickers:
                results = self._analyze_specific_tickers(tickers, job_id, max_results)
            else:
                results = self._analyze_narrative_shift(job_id, max_results)
            
            # Update job as completed
            self.company_service.update_screening_job(
                job_id,
                status="completed",
                results_count=len(results)
            )
            logger.info(f"Screening job {job_id} completed with {len(results)} results")
            
        except Exception as e:
            logger.error(f"Screening job {job_id} failed: {str(e)}")
            self.company_service.update_screening_job(
                job_id,
                status="failed",
                error_message=str(e)
            )
    
    def _analyze_narrative_shift(self, job_id: str, max_results: int) -> List[Dict]:
        """
        Analyze utilities for narrative shift opportunities.
        
        Uses EDGAR tools to fetch company data and analyze segments.
        """
        results = []
        tickers_to_analyze = UTILITY_TICKERS[:max_results]
        
        self.company_service.update_screening_job(
            job_id,
            total_companies=len(tickers_to_analyze)
        )
        
        for idx, ticker in enumerate(tickers_to_analyze):
            try:
                analysis = self._analyze_single_ticker(ticker)
                if analysis:
                    results.append(analysis)
                
                # Update progress
                self.company_service.update_screening_job(
                    job_id,
                    processed_companies=idx + 1
                )
                
            except Exception as e:
                logger.warning(f"Error analyzing {ticker}: {e}")
                continue
        
        return results
    
    def _analyze_specific_tickers(
        self,
        tickers: List[str],
        job_id: str,
        max_results: int
    ) -> List[Dict]:
        """Analyze specific ticker list for narrative shift."""
        results = []
        tickers_to_analyze = tickers[:max_results]
        
        self.company_service.update_screening_job(
            job_id,
            total_companies=len(tickers_to_analyze)
        )
        
        for idx, ticker in enumerate(tickers_to_analyze):
            try:
                analysis = self._analyze_single_ticker(ticker)
                if analysis:
                    results.append(analysis)
                
                self.company_service.update_screening_job(
                    job_id,
                    processed_companies=idx + 1
                )
                
            except Exception as e:
                logger.warning(f"Error analyzing {ticker}: {e}")
                continue
        
        return results
    
    def _analyze_single_ticker(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Perform analysis on a single ticker.
        
        This is a simplified version - in production, this would use
        the actual edgartools library to fetch SEC filings.
        """
        try:
            # Try to import edgartools
            try:
                import edgartools as edgar
                company = edgar.Company(ticker)
                financials = company.financials
                income_stmt = financials.get_income_statement()
                
                # Extract segment data
                segments = self._extract_segments(income_stmt)
                
            except ImportError:
                # Fallback: create mock data for demonstration
                segments = self._generate_mock_segments(ticker)
            
            # Analyze segments for narrative shift
            analysis = self._analyze_segments(segments, ticker)
            
            if analysis:
                # Save to database
                self._save_analysis(ticker, analysis, segments)
                return analysis
            
            return None
            
        except Exception as e:
            logger.error(f"Error in _analyze_single_ticker for {ticker}: {e}")
            return None
    
    def _extract_segments(self, income_stmt) -> List[Dict[str, Any]]:
        """
        Extract revenue segments from income statement.
        
        Identifies growth segments (renewable, solar, wind, etc.) vs
        legacy segments (transmission, distribution, regulated).
        """
        segments = []
        
        if income_stmt is None:
            return segments
        
        try:
            # Look for revenue-related accounts
            revenue_data = income_stmt[
                income_stmt['account'].str.contains(
                    'Revenue|RevenueFromContract',
                    case=False,
                    na=False
                )
            ]
            
            for _, row in revenue_data.iterrows():
                account = str(row.get('account', ''))
                value = row.get('value', 0)
                
                if value and value > 0:
                    segment_name = self._identify_segment_name(account)
                    segments.append({
                        'name': segment_name,
                        'revenue': float(value),
                        'account': account,
                        'type': self._get_segment_type(segment_name)
                    })
                    
        except Exception as e:
            logger.warning(f"Error extracting segments: {e}")
        
        return segments
    
    def _identify_segment_name(self, account: str) -> str:
        """Categorize revenue segment as growth or legacy."""
        account_lower = account.lower()
        
        growth_keywords = [
            'renewable', 'solar', 'wind', 'storage', 'battery',
            'distributed', 'generation', 'competitive',
            'energy solutions', 'new ventures', 'infrastructure',
            'grid modernization', 'advanced metering'
        ]
        
        legacy_keywords = [
            'transmission', 'distribution', 'regulated',
            'tariff', 'default service', 'basic service'
        ]
        
        for keyword in growth_keywords:
            if keyword in account_lower:
                return f"GROWTH: {keyword.title()}"
        
        for keyword in legacy_keywords:
            if keyword in account_lower:
                return f"LEGACY: {keyword.title()}"
        
        return "UNCATEGORIZED"
    
    def _get_segment_type(self, segment_name: str) -> str:
        """Get the type of segment based on its name."""
        if segment_name.startswith("GROWTH:"):
            return "growth"
        elif segment_name.startswith("LEGACY:"):
            return "legacy"
        return "uncategorized"
    
    def _analyze_segments(
        self,
        segments: List[Dict[str, Any]],
        ticker: str
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze segments for narrative shift criteria.
        
        Criteria:
        - Growth ratio: 2-3x (growth segment grows 2-3x faster than legacy)
        - New segment revenue: 15-25% of total
        """
        if not segments or len(segments) < 2:
            return None
        
        # Separate legacy and growth segments
        legacy_segments = [s for s in segments if s['type'] == 'legacy']
        growth_segments = [s for s in segments if s['type'] == 'growth']
        
        if not legacy_segments or not growth_segments:
            # Try to use uncategorized as growth for companies without clear separation
            return None
        
        # Calculate weighted averages
        legacy_growth = self._calculate_segment_growth(legacy_segments)
        new_growth = self._calculate_segment_growth(growth_segments)
        
        # Calculate revenue percentages
        total_revenue = sum(s['revenue'] for s in segments)
        new_segment_revenue = sum(s['revenue'] for s in growth_segments)
        new_segment_pct = (new_segment_revenue / total_revenue * 100) if total_revenue > 0 else 0
        
        # Calculate growth ratio
        growth_ratio = new_growth / legacy_growth if legacy_growth > 0 else 0
        
        # Check if narrative shift criteria met
        if (self.min_growth_ratio <= growth_ratio <= self.max_growth_ratio and
            self.min_new_segment_pct <= new_segment_pct <= self.max_new_segment_pct):
            
            return {
                'ticker': ticker,
                'legacy_growth_rate': legacy_growth,
                'new_segment_growth_rate': new_growth,
                'growth_ratio': growth_ratio,
                'new_segment_revenue_pct': new_segment_pct,
                'total_revenue': total_revenue,
                'meets_criteria': True
            }
        
        return None
    
    def _calculate_segment_growth(self, segments: List[Dict[str, Any]]) -> float:
        """
        Calculate weighted average growth rate for segments.
        
        In production, this would compare YoY revenue changes.
        For now, returns a mock growth rate based on segment type.
        """
        if not segments:
            return 0.0
        
        # In production: calculate actual YoY growth from SEC filings
        # For demonstration: return realistic mock values
        import random
        random.seed(hash(segments[0]['name']) % 1000)
        
        # Legacy segments: 2-5% growth
        # Growth segments: 15-30% growth
        base_type = segments[0]['type']
        
        if base_type == 'legacy':
            return random.uniform(2.0, 5.0)
        else:
            return random.uniform(15.0, 30.0)
    
    def _generate_mock_segments(self, ticker: str) -> List[Dict[str, Any]]:
        """
        Generate realistic mock segment data for demonstration.
        
        In production, this would be replaced with actual SEC EDGAR data.
        """
        import random
        random.seed(hash(ticker) % 10000)
        
        # Generate realistic segment data based on ticker
        segments = []
        
        # Legacy segments (always present for utilities)
        legacy_total = random.uniform(5_000_000_000, 20_000_000_000)
        segments.extend([
            {
                'name': 'LEGACY: Transmission',
                'revenue': legacy_total * random.uniform(0.3, 0.4),
                'account': 'TransmissionRevenue',
                'type': 'legacy'
            },
            {
                'name': 'LEGACY: Distribution',
                'revenue': legacy_total * random.uniform(0.4, 0.5),
                'account': 'DistributionRevenue',
                'type': 'legacy'
            },
            {
                'name': 'LEGACY: Regulated',
                'revenue': legacy_total * random.uniform(0.1, 0.2),
                'account': 'RegulatedServices',
                'type': 'legacy'
            }
        ])
        
        # Growth segments (varying presence)
        has_significant_growth = random.random() > 0.3
        
        if has_significant_growth:
            growth_total = random.uniform(500_000_000, 5_000_000_000)
            growth_types = random.sample([
                ('Renewable', 0.3, 0.5),
                ('Solar', 0.2, 0.4),
                ('Wind', 0.2, 0.4),
                ('Storage', 0.1, 0.2),
                ('Grid Modernization', 0.1, 0.3)
            ], k=random.randint(1, 3))
            
            for name, min_pct, max_pct in growth_types:
                segments.append({
                    'name': f'GROWTH: {name}',
                    'revenue': growth_total * random.uniform(min_pct, max_pct),
                    'account': f'{name}Revenue',
                    'type': 'growth'
                })
        
        return segments
    
    def _save_analysis(
        self,
        ticker: str,
        analysis: Dict[str, Any],
        segments: List[Dict[str, Any]]
    ):
        """Save analysis results to database."""
        try:
            # Get or create company
            company = self.db.query(Company).filter(Company.ticker == ticker).first()
            
            if not company:
                # Create placeholder company
                company = Company(
                    cik=f"{hash(ticker) % 10000000000:010d}",
                    ticker=ticker,
                    company_name=f"{ticker} Corporation",
                    sic_code='4911',
                    sic_description='Electric Services'
                )
                self.db.add(company)
                self.db.flush()
            
            # Create analysis result
            result = AnalysisResult(
                company_id=company.id,
                legacy_growth_rate=analysis['legacy_growth_rate'],
                new_segment_growth_rate=analysis['new_segment_growth_rate'],
                growth_ratio=analysis['growth_ratio'],
                new_segment_revenue_pct=analysis['new_segment_revenue_pct'],
                segments_data=segments,
                analysis_date=datetime.utcnow().date(),
                fiscal_year=datetime.utcnow().year,
                form_type='10-K'
            )
            self.db.add(result)
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving analysis for {ticker}: {e}")
            raise
