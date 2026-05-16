import React, { useEffect, useState } from 'react';
import DataTable from '../components/DataTable';
import LoadingSpinner from '../components/LoadingSpinner';
import { mockAnalysisResults } from '../services/mockData';
import { AnalysisResult } from '../types';

const Analysis: React.FC = () => {
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    minGrowthRatio: '',
    maxGrowthRatio: '',
  });

  useEffect(() => {
    const loadResults = async () => {
      setLoading(true);
      await new Promise((resolve) => setTimeout(resolve, 500));
      setResults(mockAnalysisResults);
      setLoading(false);
    };
    loadResults();
  }, []);

  const filteredResults = results.filter((r) => {
    if (
      filters.minGrowthRatio &&
      (r.growth_ratio || 0) < parseFloat(filters.minGrowthRatio)
    )
      return false;
    if (
      filters.maxGrowthRatio &&
      (r.growth_ratio || 0) > parseFloat(filters.maxGrowthRatio)
    )
      return false;
    return true;
  });

  const columns = [
    {
      key: 'company_id',
      header: 'Company',
    },
    {
      key: 'growth_ratio',
      header: 'Growth Ratio',
      render: (value: number) => (
        <span className="metric-badge">
          {value?.toFixed(2)}x
        </span>
      ),
    },
    {
      key: 'new_segment_revenue_pct',
      header: 'New Segment %',
      render: (value: number) => (
        <div className="progress-cell">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${Math.min(value || 0, 100)}%` }}
            ></div>
          </div>
          <span>{value?.toFixed(1)}%</span>
        </div>
      ),
    },
    {
      key: 'legacy_growth_rate',
      header: 'Legacy Growth',
      render: (value: number) => (
        <span className="growth-legacy">{value?.toFixed(1)}%</span>
      ),
    },
    {
      key: 'new_segment_growth_rate',
      header: 'New Growth',
      render: (value: number) => (
        <span className="growth-new">{value?.toFixed(1)}%</span>
      ),
    },
    {
      key: 'fiscal_year',
      header: 'Year',
    },
    {
      key: 'form_type',
      header: 'Form',
    },
  ];

  return (
    <div className="analysis-page">
      <div className="page-header">
        <h1>Analysis Results</h1>
        <div className="page-actions">
          <div className="filter-group">
            <label>Growth Ratio:</label>
            <input
              type="number"
              placeholder="Min"
              value={filters.minGrowthRatio}
              onChange={(e) =>
                setFilters({ ...filters, minGrowthRatio: e.target.value })
              }
              className="filter-input"
            />
            <span>to</span>
            <input
              type="number"
              placeholder="Max"
              value={filters.maxGrowthRatio}
              onChange={(e) =>
                setFilters({ ...filters, maxGrowthRatio: e.target.value })
              }
              className="filter-input"
            />
          </div>
        </div>
      </div>

      <div className="criteria-info">
        <h3>Narrative Shift Criteria</h3>
        <ul>
          <li>Growth segment grows 2-3x faster than legacy segment</li>
          <li>Growth segment represents 15-25% of total revenue</li>
        </ul>
      </div>

      {loading ? (
        <LoadingSpinner message="Loading analysis results..." />
      ) : (
        <DataTable
          columns={columns}
          data={filteredResults}
          onRowClick={(row) => console.log('View analysis:', row)}
        />
      )}
    </div>
  );
};

export default Analysis;
