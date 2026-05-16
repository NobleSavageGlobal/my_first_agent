import React, { useEffect, useState } from 'react';
import DataTable from '../components/DataTable';
import LoadingSpinner from '../components/LoadingSpinner';
import { mockCompanies } from '../services/mockData';
import { Company } from '../types';

const Companies: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    const loadCompanies = async () => {
      setLoading(true);
      await new Promise((resolve) => setTimeout(resolve, 500));
      setCompanies(mockCompanies);
      setLoading(false);
    };
    loadCompanies();
  }, []);

  const filteredCompanies = companies.filter(
    (c) =>
      c.company_name.toLowerCase().includes(filter.toLowerCase()) ||
      c.ticker?.toLowerCase().includes(filter.toLowerCase())
  );

  const columns = [
    {
      key: 'ticker',
      header: 'Ticker',
      render: (value: string) => (
        <span className="ticker-badge">{value || 'N/A'}</span>
      ),
    },
    {
      key: 'company_name',
      header: 'Company Name',
    },
    {
      key: 'cik',
      header: 'CIK',
    },
    {
      key: 'sic_code',
      header: 'SIC Code',
    },
    {
      key: 'sic_description',
      header: 'SIC Description',
    },
  ];

  return (
    <div className="companies-page">
      <div className="page-header">
        <h1>Companies</h1>
        <div className="page-actions">
          <input
            type="text"
            placeholder="Search companies..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="search-input"
          />
        </div>
      </div>

      {loading ? (
        <LoadingSpinner message="Loading companies..." />
      ) : (
        <DataTable
          columns={columns}
          data={filteredCompanies}
          onRowClick={(row) => console.log('Clicked company:', row)}
        />
      )}
    </div>
  );
};

export default Companies;
