import React from 'react';

export interface BadgeProps {
  status: string;
  size?: 'sm' | 'md' | 'lg';
}

export const Badge: React.FC<BadgeProps> = ({ status, size = 'md' }) => {
  const normalized = (status || '').toUpperCase();

  let colorClasses = 'bg-gray-100 text-gray-800 border-gray-200';

  switch (normalized) {
    case 'ACTIVE':
    case 'VERIFIED':
    case 'COMPLETED':
    case 'ACCEPTED':
    case 'RESOLVED':
      colorClasses = 'bg-emerald-50 text-emerald-700 border-emerald-200';
      break;
    case 'RESERVED':
    case 'REVIEWING':
    case 'LIKE_NEW':
      colorClasses = 'bg-amber-50 text-amber-700 border-amber-200';
      break;
    case 'SOLD':
    case 'DISMISSED':
    case 'GOOD':
      colorClasses = 'bg-blue-50 text-blue-700 border-blue-200';
      break;
    case 'PENDING':
    case 'OPEN':
    case 'NEW':
      colorClasses = 'bg-indigo-50 text-indigo-700 border-indigo-200';
      break;
    case 'REJECTED':
    case 'CANCELLED':
    case 'REMOVED':
    case 'SUSPENDED':
    case 'POOR':
      colorClasses = 'bg-rose-50 text-rose-700 border-rose-200';
      break;
    case 'FAIR':
      colorClasses = 'bg-orange-50 text-orange-700 border-orange-200';
      break;
    default:
      colorClasses = 'bg-slate-100 text-slate-700 border-slate-200';
  }

  const sizeClasses =
    size === 'sm'
      ? 'px-2 py-0.5 text-xs font-semibold'
      : size === 'lg'
      ? 'px-3 py-1 text-sm font-semibold'
      : 'px-2.5 py-1 text-xs font-semibold';

  return (
    <span
      className={`inline-flex items-center rounded-full border shadow-xs transition-colors ${colorClasses} ${sizeClasses}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5 opacity-75" />
      {normalized.replace('_', ' ')}
    </span>
  );
};
