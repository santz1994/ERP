/**
 * NavigationCard Component
 * Purpose: Reusable card component for module landing pages
 * Usage: Link to detail pages with icon, title, description
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LucideIcon, ChevronRight } from 'lucide-react';
import { Card } from './card';
import { cn } from '@/lib/utils';

interface NavigationCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  link?: string; // Made optional
  color?: 'purple' | 'blue' | 'green' | 'orange' | 'red' | 'yellow' | 'gray';
  badge?: string;
  disabled?: boolean;
  onClick?: () => void;
}

const colorClasses = {
  purple: {
    bg: 'bg-purple-50 hover:bg-purple-100',
    border: 'border-purple-200 hover:border-purple-300',
    icon: 'text-purple-600',
    iconBg: 'bg-purple-100',
    text: 'text-purple-700',
  },
  blue: {
    bg: 'bg-blue-50 hover:bg-blue-100',
    border: 'border-blue-200 hover:border-blue-300',
    icon: 'text-blue-600',
    iconBg: 'bg-blue-100',
    text: 'text-blue-700',
  },
  green: {
    bg: 'bg-green-50 hover:bg-green-100',
    border: 'border-green-200 hover:border-green-300',
    icon: 'text-green-600',
    iconBg: 'bg-green-100',
    text: 'text-green-700',
  },
  orange: {
    bg: 'bg-orange-50 hover:bg-orange-100',
    border: 'border-orange-200 hover:border-orange-300',
    icon: 'text-orange-600',
    iconBg: 'bg-orange-100',
    text: 'text-orange-700',
  },
  red: {
    bg: 'bg-red-50 hover:bg-red-100',
    border: 'border-red-200 hover:border-red-300',
    icon: 'text-red-600',
    iconBg: 'bg-red-100',
    text: 'text-red-700',
  },
  yellow: {
    bg: 'bg-yellow-50 hover:bg-yellow-100',
    border: 'border-yellow-200 hover:border-yellow-300',
    icon: 'text-yellow-600',
    iconBg: 'bg-yellow-100',
    text: 'text-yellow-700',
  },
  gray: {
    bg: 'bg-gray-50 hover:bg-gray-100',
    border: 'border-gray-200 hover:border-gray-300',
    icon: 'text-gray-600',
    iconBg: 'bg-gray-100',
    text: 'text-gray-700',
  },
};

export const NavigationCard: React.FC<NavigationCardProps> = ({
  title,
  description,
  icon: Icon,
  link,
  color = 'blue',
  badge,
  disabled = false,
  onClick,
}) => {
  const navigate = useNavigate();
  const colors = colorClasses[color];

  const handleClick = () => {
    if (disabled) return;
    
    if (onClick) {
      onClick();
    } else if (link) {
      navigate(link);
    }
  };

  return (
    <Card
      className={cn(
        'border-2 transition-all duration-200 cursor-pointer group',
        colors.bg,
        colors.border,
        disabled && 'opacity-50 cursor-not-allowed',
        !disabled && 'hover:shadow-md transform hover:scale-[1.02]'
      )}
      onClick={handleClick}
    >
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className={cn('p-3 rounded-lg', colors.iconBg)}>
            <Icon className={cn('h-6 w-6', colors.icon)} />
          </div>
          {badge && (
            <span className={cn(
              'px-2 py-1 text-xs font-medium rounded-full',
              colors.iconBg,
              colors.text
            )}>
              {badge}
            </span>
          )}
          {!disabled && (
            <ChevronRight className={cn(
              'h-5 w-5 transition-transform group-hover:translate-x-1',
              colors.icon
            )} />
          )}
        </div>

        <h3 className={cn('text-lg font-semibold mb-2', colors.text)}>
          {title}
        </h3>
        
        <p className="text-sm text-gray-600">
          {description}
        </p>

        {disabled && (
          <div className="mt-3 text-xs text-gray-500 italic">
            Coming soon...
          </div>
        )}
      </div>
    </Card>
  );
};

export default NavigationCard;
