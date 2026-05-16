-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cik VARCHAR(20) UNIQUE NOT NULL,
    ticker VARCHAR(10),
    company_name VARCHAR(500) NOT NULL,
    sic_code VARCHAR(10),
    sic_description VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Analysis results table
CREATE TABLE IF NOT EXISTS analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    legacy_growth_rate DECIMAL(10, 4),
    new_segment_growth_rate DECIMAL(10, 4),
    growth_ratio DECIMAL(10, 4),
    new_segment_revenue_pct DECIMAL(10, 4),
    segments_data JSONB,
    analysis_date DATE NOT NULL,
    fiscal_year INTEGER,
    form_type VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Screening jobs table
CREATE TABLE IF NOT EXISTS screening_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    total_companies INTEGER DEFAULT 0,
    processed_companies INTEGER DEFAULT 0,
    results_count INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Favorite companies for users
CREATE TABLE IF NOT EXISTS favorites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_companies_ticker ON companies(ticker);
CREATE INDEX IF NOT EXISTS idx_companies_sic ON companies(sic_code);
CREATE INDEX IF NOT EXISTS idx_analysis_results_company ON analysis_results(company_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_date ON analysis_results(analysis_date);
CREATE INDEX IF NOT EXISTS idx_screening_jobs_status ON screening_jobs(status);

-- Comments for documentation
COMMENT ON TABLE companies IS 'SEC registered companies';
COMMENT ON TABLE analysis_results IS 'Narrative shift analysis results for companies';
COMMENT ON TABLE screening_jobs IS 'Background job tracking for screening operations';
COMMENT ON TABLE favorites IS 'User favorite companies';
