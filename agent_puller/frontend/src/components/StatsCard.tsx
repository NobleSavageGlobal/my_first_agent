import React from 'react';

interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: string;
  trend?: 'up' | 'down' | 'neutral';
}

const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
}) => {
  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'text-success';
      case 'down':
        return 'text-danger';
      default:
        return 'text-muted';
    }
  };

  return (
    <div className="stats-card">
      <div className="stats-header">
        {icon && <span className="stats-icon">{icon}</span>}
        <h3 className="stats-title">{title}</h3>
      </div>
      <div className="stats-body">
        <span className={`stats-value ${getTrendColor()}`}>{value}</span>
        {subtitle && <span className="stats-subtitle">{subtitle}</span>}
      </div>
    </div>
  );
};

export default StatsCard;
