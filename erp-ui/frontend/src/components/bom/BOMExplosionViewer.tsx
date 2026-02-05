/**
 * BOM Explosion Viewer - Visual MO to WO Material Flow
 * Priority 2.3: BOM Management UI
 * Created: 2026-02-04
 */

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { 
  ArrowRight, 
  Package, 
  Factory, 
  Boxes,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Eye,
  DollarSign
} from 'lucide-react';

interface ExplosionNode {
  level: number;
  product_id: number;
  product_code: string;
  product_name: string;
  product_type: string;
  qty_required: number;
  uom: string;
  department?: string;
  work_order_id?: number;
  work_order_code?: string;
  material_cost?: number;
  total_cost?: number;
  children?: ExplosionNode[];
}

interface BOMExplosionViewerProps {
  moId: number;
  showCosts?: boolean;
}

export const BOMExplosionViewer: React.FC<BOMExplosionViewerProps> = ({ 
  moId,
  showCosts = false 
}) => {
  const [expandedNodes, setExpandedNodes] = useState<Set<number>>(new Set([0])); // Start with root expanded

  // Fetch MO Details
  const { data: moDetails, isLoading: moLoading } = useQuery({
    queryKey: ['mo-details', moId],
    queryFn: async () => {
      const response = await apiClient.get(`/ppic/manufacturing-order/${moId}`);
      return response.data;
    }
  });

  // Fetch BOM Explosion from MO
  const { data: explosion, isLoading: explosionLoading } = useQuery({
    queryKey: ['bom-explosion-mo', moId],
    queryFn: async () => {
      const response = await apiClient.get(`/ppic/manufacturing-order/${moId}/explosion`);
      return response.data as ExplosionNode[];
    }
  });

  // Fetch Work Orders for this MO
  const { data: workOrders } = useQuery({
    queryKey: ['work-orders-for-mo', moId],
    queryFn: async () => {
      const response = await apiClient.get(`/work-orders?mo_id=${moId}`);
      return response.data;
    }
  });

  const toggleNode = (level: number) => {
    setExpandedNodes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(level)) {
        newSet.delete(level);
      } else {
        newSet.add(level);
      }
      return newSet;
    });
  };

  const expandAll = () => {
    if (explosion) {
      const allLevels = new Set<number>();
      const collectLevels = (nodes: ExplosionNode[]) => {
        nodes.forEach(node => {
          allLevels.add(node.level);
          if (node.children) collectLevels(node.children);
        });
      };
      collectLevels(explosion);
      setExpandedNodes(allLevels);
    }
  };

  const collapseAll = () => {
    setExpandedNodes(new Set([0])); // Keep root expanded
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'RAW': return 'text-green-600 bg-green-50';
      case 'WIP': return 'text-blue-600 bg-blue-50';
      case 'Finish Good': return 'text-purple-600 bg-purple-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'RAW': return '';
      case 'WIP': return '';
      case 'Finish Good': return '';
      default: return '[File]';
    }
  };

  const renderNode = (node: ExplosionNode, depth: number = 0) => {
    const hasChildren = node.children && node.children.length > 0;
    const isExpanded = expandedNodes.has(node.level);
    const indent = depth * 48;

    const workOrder = workOrders?.find((wo: any) => wo.product_id === node.product_id);

    return (
      <div key={`${node.level}-${node.product_id}`} className="relative">
        {/* Connector Lines */}
        {depth > 0 && (
          <div 
            className="absolute left-0 top-1/2 w-8 border-t-2 border-gray-300"
            style={{ left: `${indent - 32}px` }}
          />
        )}

        <div
          className={`flex items-center gap-4 py-4 px-4 rounded-lg hover:bg-gray-50 transition-all ${
            depth === 0 ? 'bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-300' : ''
          }`}
          style={{ paddingLeft: `${indent + 16}px` }}
        >
          {/* Level Badge */}
          <div className="flex-shrink-0">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm ${
              depth === 0 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
            }`}>
              L{node.level}
            </div>
          </div>

          {/* Product Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xl">{getTypeIcon(node.product_type)}</span>
              <h4 className="font-bold text-gray-900">{node.product_code}</h4>
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${getTypeColor(node.product_type)}`}>
                {node.product_type}
              </span>
              {node.department && (
                <span className="px-2 py-0.5 bg-orange-100 text-orange-800 rounded text-xs font-semibold">
                  {node.department}
                </span>
              )}
            </div>
            <p className="text-sm text-gray-600 truncate">{node.product_name}</p>
          </div>

          {/* Quantity & Cost */}
          <div className="flex-shrink-0 text-right">
            <div className="flex items-center gap-2">
              <div>
                <div className="text-lg font-bold text-gray-900">
                  {node.qty_required.toFixed(2)} {node.uom}
                </div>
                {showCosts && node.material_cost && (
                  <div className="text-xs text-gray-600 flex items-center gap-1">
                    <DollarSign size={12} />
                    ${(node.material_cost * node.qty_required).toFixed(2)}
                  </div>
                )}
              </div>
              {hasChildren && (
                <button
                  onClick={() => toggleNode(node.level + 1)}
                  className="p-2 hover:bg-gray-200 rounded-full transition-colors"
                >
                  <ArrowRight 
                    size={20} 
                    className={`transition-transform ${isExpanded ? 'rotate-90' : ''}`}
                  />
                </button>
              )}
            </div>
          </div>

          {/* Work Order Badge */}
          {workOrder && (
            <div className="flex-shrink-0">
              <div className={`px-3 py-1 rounded-lg text-xs font-semibold flex items-center gap-1 ${
                workOrder.state === 'COMPLETED' ? 'bg-green-100 text-green-800' :
                workOrder.state === 'RUNNING' ? 'bg-blue-100 text-blue-800' :
                workOrder.state === 'READY' ? 'bg-purple-100 text-purple-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {workOrder.state === 'COMPLETED' ? <CheckCircle size={12} /> : 
                 workOrder.state === 'RUNNING' ? <Factory size={12} /> :
                 <AlertTriangle size={12} />}
                {workOrder.wo_code}
              </div>
            </div>
          )}
        </div>

        {/* Render Children */}
        {hasChildren && isExpanded && (
          <div className="relative">
            {/* Vertical connector line */}
            <div 
              className="absolute left-0 top-0 bottom-0 w-0.5 bg-gray-300"
              style={{ left: `${indent + 20}px` }}
            />
            {node.children!.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  if (moLoading || explosionLoading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading BOM explosion...</p>
        </div>
      </div>
    );
  }

  const totalCost = explosion?.reduce((sum, node) => {
    const calcNodeCost = (n: ExplosionNode): number => {
      let cost = (n.material_cost || 0) * n.qty_required;
      if (n.children) {
        cost += n.children.reduce((childSum, child) => childSum + calcNodeCost(child), 0);
      }
      return cost;
    };
    return sum + calcNodeCost(node);
  }, 0);

  return (
    <div className="bg-white rounded-lg shadow-md">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="bg-purple-100 p-2 rounded-lg">
              <Boxes className="text-purple-600" size={24} />
            </div>
            <div>
              <h3 className="text-lg font-bold text-gray-900">BOM Explosion Viewer</h3>
              <p className="text-sm text-gray-600">Multi-level material requirements</p>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={expandAll}
              className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
            >
              Expand All
            </button>
            <button
              onClick={collapseAll}
              className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
            >
              Collapse All
            </button>
          </div>
        </div>

        {/* MO Summary */}
        {moDetails && (
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 grid grid-cols-5 gap-4 text-sm">
            <div>
              <div className="text-gray-600">MO Number</div>
              <div className="font-bold text-gray-900">MO-{moDetails.id.toString().padStart(6, '0')}</div>
            </div>
            <div>
              <div className="text-gray-600">Product</div>
              <div className="font-bold text-gray-900">{moDetails.product_code}</div>
            </div>
            <div>
              <div className="text-gray-600">Quantity</div>
              <div className="font-bold text-gray-900">{moDetails.qty_planned} pcs</div>
            </div>
            <div>
              <div className="text-gray-600">State</div>
              <div className={`font-bold ${
                moDetails.state === 'COMPLETED' ? 'text-green-600' :
                moDetails.state === 'IN_PROGRESS' ? 'text-blue-600' :
                'text-gray-600'
              }`}>
                {moDetails.state}
              </div>
            </div>
            {showCosts && (
              <div>
                <div className="text-gray-600">Total Material Cost</div>
                <div className="font-bold text-green-600 flex items-center gap-1">
                  <DollarSign size={14} />
                  {totalCost?.toFixed(2) || '0.00'}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Explosion Tree */}
      <div className="p-6">
        {!explosion || explosion.length === 0 ? (
          <div className="text-center py-12">
            <AlertTriangle className="mx-auto text-gray-400 mb-4" size={64} />
            <h4 className="text-lg font-semibold text-gray-900 mb-2">No BOM Explosion Data</h4>
            <p className="text-gray-600">BOM structure not available for this MO</p>
          </div>
        ) : (
          <div className="space-y-2">
            {explosion.map(node => renderNode(node, 0))}
          </div>
        )}
      </div>

      {/* Footer Stats */}
      {explosion && explosion.length > 0 && (
        <div className="px-6 py-3 bg-gray-50 border-t rounded-b-lg">
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <TrendingDown className="text-blue-600" size={18} />
              <div>
                <div className="text-gray-600">Total Levels</div>
                <div className="font-bold text-gray-900">
                  {Math.max(...explosion.map(n => {
                    let maxLevel = n.level;
                    const getMaxLevel = (node: ExplosionNode): number => {
                      if (node.children) {
                        return Math.max(node.level, ...node.children.map(getMaxLevel));
                      }
                      return node.level;
                    };
                    return getMaxLevel(n);
                  }))}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Package className="text-green-600" size={18} />
              <div>
                <div className="text-gray-600">Work Orders</div>
                <div className="font-bold text-gray-900">{workOrders?.length || 0}</div>
              </div>
            </div>
            {showCosts && (
              <div className="flex items-center gap-2">
                <DollarSign className="text-purple-600" size={18} />
                <div>
                  <div className="text-gray-600">Material Cost</div>
                  <div className="font-bold text-green-600">${totalCost?.toFixed(2) || '0.00'}</div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
