import React from 'react';
import { AnalysisResult, Company } from '../types';

interface DataTableProps {
  columns: {
    key: string;
    header: string;
    render?: (value: any, row: any) => React.ReactNode;
  }[];
  data: any[];
  onRowClick?: (row: any) => void;
  loading?: boolean;
}

const DataTable: React.FC<DataTableProps> = ({
  columns,
  data,
  onRowClick,
  loading,
}) => {
  if (loading) {
    return (
      <div className="table-loading">
        <div className="spinner"></div>
        <span>Loading data...</span>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="table-empty">
        <span>No data available</span>
      </div>
    );
  }

  return (
    <div className="table-container">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key}>{col.header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr
              key={idx}
              onClick={() => onRowClick?.(row)}
              className={onRowClick ? 'clickable' : ''}
            >
              {columns.map((col) => (
                <td key={col.key}>
                  {col.render
                    ? col.render(row[col.key], row)
                    : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;
