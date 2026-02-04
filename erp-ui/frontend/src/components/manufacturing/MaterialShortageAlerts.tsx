/**
 * Material Shortage Alerts Widget
 * Priority 1.4: Real-time Material Shortage Monitoring
 * Created: 2026-02-04
 */

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { AlertTriangle, Package, TrendingUp, RefreshCw, ExternalLink } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface MaterialShortage {
  id: number;
  material_id: number;
  material_code: string;
  material_name: string;
  required_qty: number;
  available_qty: number;
  shortage_qty: number;
  uom: string;
  wo_id: number;
  wo_code: string;
  department: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM';
  created_at: string;
}

interface MaterialShortageAlertsProps {
  showAll?: boolean;
  maxItems?: number;
}

export const MaterialShortageAlerts: React.FC<MaterialShortageAlertsProps> = ({ 
  showAll = false, 
  maxItems = 5 
}) => {
  const navigate = useNavigate();
  const [expanded, setExpanded] = useState(false);

  // Fetch material shortages
  const { data: shortages, isLoading, refetch } = useQuery({
    queryKey: ['material-shortages'],
    queryFn: async () => {
      const response = await apiClient.get('/material-allocation/shortages');
      return response.data as MaterialShortage[];
    },
    refetchInterval: 10000 // Refresh every 10 seconds
  });

  const criticalCount = shortages?.filter(s => s.severity === 'CRITICAL').length || 0;
  const highCount = shortages?.filter(s => s.severity === 'HIGH').length || 0;
  const totalCount = shortages?.length || 0;

  const displayedShortages = expanded || showAll 
    ? shortages 
    : shortages?.slice(0, maxItems);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return 'bg-red-100 text-red-800 border-red-300';
      case 'HIGH': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'MEDIUM': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return '🚨';
      case 'HIGH': return '⚠️';
      case 'MEDIUM': return '⚡';
      default: return '📦';
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            <div className="h-20 bg-gray-100 rounded"></div>
            <div className="h-20 bg-gray-100 rounded"></div>
            <div className="h-20 bg-gray-100 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-red-100 p-2 rounded-lg">
            <AlertTriangle className="text-red-600" size={24} />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900">Material Shortages</h3>
            <p className="text-sm text-gray-600">Real-time alerts</p>
          </div>
        </div>
        <button
          onClick={() => refetch()}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          title="Refresh"
        >
          <RefreshCw size={20} className="text-gray-600" />
        </button>
      </div>

      {/* Summary Stats */}
      {totalCount > 0 && (
        <div className="px-6 py-3 bg-gradient-to-r from-red-50 to-orange-50 border-b grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{criticalCount}</div>
            <div className="text-xs text-gray-600">Critical</div>
          </div>
          <div className="text-center border-l border-r border-gray-200">
            <div className="text-2xl font-bold text-orange-600">{highCount}</div>
            <div className="text-xs text-gray-600">High</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-700">{totalCount}</div>
            <div className="text-xs text-gray-600">Total</div>
          </div>
        </div>
      )}

      {/* Shortage List */}
      <div className="p-6">
        {totalCount === 0 ? (
          <div className="text-center py-12">
            <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Package className="text-green-600" size={32} />
            </div>
            <h4 className="text-lg font-semibold text-gray-900 mb-2">All Clear!</h4>
            <p className="text-gray-600">No material shortages detected</p>
          </div>
        ) : (
          <div className="space-y-3">
            {displayedShortages?.map((shortage) => (
              <div
                key={shortage.id}
                className={`border-2 rounded-lg p-4 transition-all hover:shadow-md ${getSeverityColor(shortage.severity)}`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-2xl">{getSeverityIcon(shortage.severity)}</span>
                      <h4 className="font-bold text-gray-900">
                        {shortage.material_code}
                      </h4>
                      <span className={`px-2 py-1 text-xs font-semibold rounded ${
                        shortage.severity === 'CRITICAL' ? 'bg-red-200 text-red-800' :
                        shortage.severity === 'HIGH' ? 'bg-orange-200 text-orange-800' :
                        'bg-yellow-200 text-yellow-800'
                      }`}>
                        {shortage.severity}
                      </span>
                    </div>
                    
                    <p className="text-sm text-gray-700 mb-2">{shortage.material_name}</p>
                    
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>
                        <span className="text-gray-600">Required:</span>
                        <span className="font-semibold ml-1">
                          {shortage.required_qty.toFixed(2)} {shortage.uom}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Available:</span>
                        <span className="font-semibold ml-1">
                          {shortage.available_qty.toFixed(2)} {shortage.uom}
                        </span>
                      </div>
                      <div className="col-span-2">
                        <span className="text-gray-600">Shortage:</span>
                        <span className="font-bold text-red-700 ml-1">
                          -{shortage.shortage_qty.toFixed(2)} {shortage.uom}
                        </span>
                      </div>
                    </div>

                    <div className="mt-2 pt-2 border-t border-gray-300 flex items-center gap-4 text-xs text-gray-600">
                      <span>🏭 {shortage.department}</span>
                      <span>📋 {shortage.wo_code}</span>
                    </div>
                  </div>

                  <button
                    onClick={() => navigate(`/warehouse?material=${shortage.material_id}`)}
                    className="flex-shrink-0 p-2 hover:bg-white/50 rounded-lg transition-colors"
                    title="View in Warehouse"
                  >
                    <ExternalLink size={18} />
                  </button>
                </div>
              </div>
            ))}

            {/* Show More/Less Button */}
            {!showAll && shortages && shortages.length > maxItems && (
              <button
                onClick={() => setExpanded(!expanded)}
                className="w-full py-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                {expanded ? 'Show Less' : `Show ${shortages.length - maxItems} More`}
              </button>
            )}
          </div>
        )}
      </div>

      {/* Action Footer */}
      {totalCount > 0 && (
        <div className="px-6 py-3 bg-gray-50 border-t rounded-b-lg flex items-center justify-between">
          <p className="text-xs text-gray-600">
            Last updated: {new Date().toLocaleTimeString()}
          </p>
          <button
            onClick={() => navigate('/purchasing')}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
          >
            Create Purchase Order
            <TrendingUp size={16} />
          </button>
        </div>
      )}
    </div>
  );
};
