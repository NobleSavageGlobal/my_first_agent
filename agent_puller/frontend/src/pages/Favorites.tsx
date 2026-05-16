import React, { useEffect, useState } from 'react';
import DataTable from '../components/DataTable';
import LoadingSpinner from '../components/LoadingSpinner';
import { Favorite, Company } from '../types';

const Favorites: React.FC = () => {
  const [favorites, setFavorites] = useState<(Favorite & { company?: Company })[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadFavorites = async () => {
      setLoading(true);
      await new Promise((resolve) => setTimeout(resolve, 500));
      // Mock favorites with companies
      setFavorites([
        {
          id: '1',
          company_id: '1',
          notes: 'Strong renewable growth, watch for capex announcements',
          created_at: '2024-01-14T10:00:00Z',
          company: {
            id: '1',
            cik: '0000753948',
            ticker: 'NEE',
            company_name: 'NextEra Energy, Inc.',
            sic_code: '4911',
            sic_description: 'Electric Services',
            created_at: '2024-01-15T10:00:00Z',
            updated_at: '2024-01-15T10:00:00Z',
          },
        },
        {
          id: '2',
          company_id: '5',
          notes: 'Battery storage focus, high growth potential',
          created_at: '2024-01-13T10:00:00Z',
          company: {
            id: '5',
            cik: '0000820043',
            ticker: 'VST',
            company_name: 'Vistra Corp.',
            sic_code: '4911',
            sic_description: 'Electric Services',
            created_at: '2024-01-15T10:00:00Z',
            updated_at: '2024-01-15T10:00:00Z',
          },
        },
      ]);
      setLoading(false);
    };
    loadFavorites();
  }, []);

  const handleRemoveFavorite = async (favoriteId: string) => {
    if (window.confirm('Remove this company from favorites?')) {
      setFavorites((prev) => prev.filter((f) => f.id !== favoriteId));
    }
  };

  const columns = [
    {
      key: 'company',
      header: 'Company',
      render: (_: any, row: Favorite & { company?: Company }) => (
        <div className="company-cell">
          <span className="ticker-badge">{row.company?.ticker || 'N/A'}</span>
          <span className="company-name">{row.company?.company_name || 'Unknown'}</span>
        </div>
      ),
    },
    {
      key: 'notes',
      header: 'Notes',
    },
    {
      key: 'created_at',
      header: 'Added',
      render: (value: string) => new Date(value).toLocaleDateString(),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (_: any, row: Favorite) => (
        <button
          className="btn btn-small btn-danger"
          onClick={(e) => {
            e.stopPropagation();
            handleRemoveFavorite(row.id);
          }}
        >
          Remove
        </button>
      ),
    },
  ];

  return (
    <div className="favorites-page">
      <div className="page-header">
        <h1>Favorites</h1>
        <p className="page-subtitle">Companies you've saved for later review</p>
      </div>

      {loading ? (
        <LoadingSpinner message="Loading favorites..." />
      ) : favorites.length === 0 ? (
        <div className="empty-state">
          <p>No favorites yet. Add companies from the Analysis page.</p>
        </div>
      ) : (
        <DataTable columns={columns} data={favorites} />
      )}
    </div>
  );
};

export default Favorites;
