import React, { useEffect, useState } from 'react';
import StatsCard from '../components/StatsCard';
import DataTable from '../components/DataTable';
import LoadingSpinner from '../components/LoadingSpinner';
import { mockDashboardStats, mockAnalysisResults, mockScreeningJobs } from '../services/mockData';
import { DashboardStats, AnalysisResult, ScreeningJob } from '../types';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentResults, setRecentResults] = useState<AnalysisResult[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API call
    const loadDashboard = async () => {
      setLoading(true);
      await new Promise((resolve) => setTimeout(resolve, 500));
      setStats(mockDashboardStats);
      setRecentResults(mockAnalysisResults.slice(0, 5));
      setLoading(false);
    };

    loadDashboard();
  }, []);

  if (loading) {
    return <LoadingSpinner message="Loading dashboard..." />;
  }

  const jobColumns = [
    {
      key: 'job_type',
      header: 'Job Type',
      render: (value: string) => (
        <span className="badge badge-primary">{value}</span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (value: string) => (
        <span className={`badge badge-${value === 'completed' ? 'success' : value === 'running' ? 'info' : 'warning'}`}>
          {value}
        </span>
      ),
    },
    {
      key: 'processed_companies',
      header: 'Progress',
      render: (_: any, row: ScreeningJob) => (
        <div className="progress-cell">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{
                width: `${(row.processed_companies / row.total_companies) * 100}%`,
              }}
            ></div>
          </div>
          <span>
            {row.processed_companies}/{row.total_companies}
          </span>
        </div>
      ),
    },
    {
      key: 'results_count',
      header: 'Results',
    },
    {
      key: 'created_at',
      header: 'Created',
      render: (value: string) => new Date(value).toLocaleString(),
    },
  ];

  return (
    <div className="dashboard">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p className="page-subtitle">Overview of narrative shift analysis</p>
      </div>

      <div className="stats-grid">
        <StatsCard
          title="Total Companies"
          value={stats?.total_companies || 0}
          icon="🏢"
          subtitle="In database"
        />
        <StatsCard
          title="Total Analyses"
          value={stats?.total_analyses || 0}
          icon="📊"
          subtitle="All time"
        />
        <StatsCard
          title="Narrative Shifts"
          value={stats?.narrative_shifts_found || 0}
          icon="📈"
          trend="up"
          subtitle="Found"
        />
        <StatsCard
          title="Active Jobs"
          value={stats?.recent_jobs.filter((j) => j.status === 'running').length || 0}
          icon="⚙️"
          subtitle="Running"
        />
      </div>

      <div className="dashboard-sections">
        <section className="dashboard-section">
          <h2>Recent Analysis Results</h2>
          <DataTable
            columns={[
              {
                key: 'company_id',
                header: 'Company ID',
              },
              {
                key: 'growth_ratio',
                header: 'Growth Ratio',
                render: (value: number) => (
                  <span className="growth-ratio">{value?.toFixed(2)}x</span>
                ),
              },
              {
                key: 'new_segment_revenue_pct',
                header: 'New Segment %',
                render: (value: number) => `${value?.toFixed(1)}%`,
              },
              {
                key: 'legacy_growth_rate',
                header: 'Legacy Growth',
                render: (value: number) => `${value?.toFixed(1)}%`,
              },
              {
                key: 'new_segment_growth_rate',
                header: 'New Segment Growth',
                render: (value: number) => `${value?.toFixed(1)}%`,
              },
              {
                key: 'analysis_date',
                header: 'Analysis Date',
              },
            ]}
            data={recentResults}
          />
        </section>

        <section className="dashboard-section">
          <h2>Recent Screening Jobs</h2>
          <DataTable columns={jobColumns} data={stats?.recent_jobs || []} />
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
