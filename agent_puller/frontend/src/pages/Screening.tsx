import React, { useState } from 'react';
import LoadingSpinner from '../components/LoadingSpinner';
import { ScreeningJob } from '../types';
import { mockScreeningJobs } from '../services/mockData';

const Screening: React.FC = () => {
  const [jobType, setJobType] = useState<'narrative_shift' | 'specific_tickers'>('narrative_shift');
  const [tickers, setTickers] = useState('');
  const [maxResults, setMaxResults] = useState(100);
  const [loading, setLoading] = useState(false);
  const [jobs, setJobs] = useState<ScreeningJob[]>(mockScreeningJobs);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleStartScreening = async () => {
    setLoading(true);
    setMessage(null);

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1500));

      const newJob: ScreeningJob = {
        id: Date.now().toString(),
        job_type: jobType,
        status: 'pending',
        total_companies: maxResults,
        processed_companies: 0,
        results_count: 0,
        error_message: null,
        started_at: null,
        completed_at: null,
        created_at: new Date().toISOString(),
      };

      setJobs([newJob, ...jobs]);
      setMessage({ type: 'success', text: 'Screening job started successfully!' });

      // Simulate job progress
      simulateJobProgress(newJob.id);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to start screening job' });
    } finally {
      setLoading(false);
    }
  };

  const simulateJobProgress = (jobId: string) => {
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 10;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        setJobs((prev) =>
          prev.map((j) =>
            j.id === jobId
              ? {
                  ...j,
                  status: 'completed',
                  processed_companies: j.total_companies,
                  results_count: Math.floor(Math.random() * 20) + 5,
                  completed_at: new Date().toISOString(),
                }
              : j
          )
        );
      } else {
        setJobs((prev) =>
          prev.map((j) =>
            j.id === jobId
              ? {
                  ...j,
                  status: 'running',
                  processed_companies: Math.floor((progress / 100) * j.total_companies),
                  started_at: j.started_at || new Date().toISOString(),
                }
              : j
          )
        );
      }
    }, 500);
  };

  return (
    <div className="screening-page">
      <div className="page-header">
        <h1>Run Screening</h1>
        <p className="page-subtitle">Start a new narrative shift analysis</p>
      </div>

      {message && (
        <div className={`message message-${message.type}`}>{message.text}</div>
      )}

      <div className="screening-form">
        <div className="form-section">
          <h3>Screening Type</h3>
          <div className="radio-group">
            <label className="radio-label">
              <input
                type="radio"
                name="jobType"
                value="narrative_shift"
                checked={jobType === 'narrative_shift'}
                onChange={() => setJobType('narrative_shift')}
              />
              <span className="radio-text">
                <strong>Narrative Shift Analysis</strong>
                <small>Analyze utility companies for narrative shift opportunities</small>
              </span>
            </label>
            <label className="radio-label">
              <input
                type="radio"
                name="jobType"
                value="specific_tickers"
                checked={jobType === 'specific_tickers'}
                onChange={() => setJobType('specific_tickers')}
              />
              <span className="radio-text">
                <strong>Specific Tickers</strong>
                <small>Analyze a custom list of ticker symbols</small>
              </span>
            </label>
          </div>
        </div>

        {jobType === 'specific_tickers' && (
          <div className="form-section">
            <h3>Ticker Symbols</h3>
            <textarea
              placeholder="Enter ticker symbols, one per line (e.g., NEE, DUK, SO)"
              value={tickers}
              onChange={(e) => setTickers(e.target.value)}
              className="tickers-input"
            />
          </div>
        )}

        <div className="form-section">
          <h3>Parameters</h3>
          <div className="form-row">
            <label>
              Max Results:
              <input
                type="number"
                value={maxResults}
                onChange={(e) => setMaxResults(parseInt(e.target.value) || 100)}
                min={1}
                max={500}
                className="number-input"
              />
            </label>
          </div>
        </div>

        <button
          onClick={handleStartScreening}
          disabled={loading}
          className="btn btn-primary"
        >
          {loading ? <LoadingSpinner size="small" /> : 'Start Screening'}
        </button>
      </div>

      <div className="jobs-section">
        <h2>Screening Jobs</h2>
        <div className="jobs-list">
          {jobs.map((job) => (
            <div key={job.id} className="job-card">
              <div className="job-header">
                <span className={`badge badge-${job.status === 'completed' ? 'success' : job.status === 'running' ? 'info' : 'warning'}`}>
                  {job.status}
                </span>
                <span className="job-type">{job.job_type}</span>
              </div>
              <div className="job-progress">
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${(job.processed_companies / job.total_companies) * 100}%`,
                    }}
                  ></div>
                </div>
                <span className="progress-text">
                  {job.processed_companies} / {job.total_companies} companies
                </span>
              </div>
              {job.results_count > 0 && (
                <div className="job-results">
                  {job.results_count} results found
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Screening;
