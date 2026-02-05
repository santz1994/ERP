/**
 * BOM Explorer - Multi-level BOM Tree View
 * Priority 2.1: BOM Management UI
 * Created: 2026-02-04
 */

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { 
  ChevronRight, 
  ChevronDown, 
  Package, 
  Boxes, 
  Info,
  Search,
  Filter,
  Eye
} from 'lucide-react';

interface BOMComponent {
  id: number;
  component_id: number;
  component_code: string;
  component_name: string;
  component_type: string;
  quantity: number;
  uom: string;
  level: number;
  sequence: number;
  department?: string;
  children?: BOMComponent[];
}

interface BOMHeader {
  id: number;
  product_id: number;
  product_code: string;
  product_name: string;
  version: string;
  state: string;
  total_components: number;
  created_at: string;
}

interface BOMExplorerProps {
  productId?: number;
  showSearch?: boolean;
}

export const BOMExplorer: React.FC<BOMExplorerProps> = ({ 
  productId,
  showSearch = true 
}) => {
  const [selectedProduct, setSelectedProduct] = useState<number | undefined>(productId);
  const [expandedNodes, setExpandedNodes] = useState<Set<number>>(new Set());
  const [searchTerm, setSearchTerm] = useState('');
  const [departmentFilter, setDepartmentFilter] = useState<string>('ALL');

  // Fetch products for selection
  const { data: products } = useQuery({
    queryKey: ['products-with-bom'],
    queryFn: async () => {
      const response = await apiClient.get('/admin/products?has_bom=true');
      return response.data.products;
    },
    enabled: showSearch
  });

  // Fetch BOM header
  const { data: bomHeader, isLoading: bomHeaderLoading } = useQuery({
    queryKey: ['bom-header', selectedProduct],
    queryFn: async () => {
      const response = await apiClient.get(`/bom/${selectedProduct}`);
      return response.data as BOMHeader;
    },
    enabled: !!selectedProduct
  });

  // Fetch BOM explosion (multi-level)
  const { data: bomTree, isLoading: bomTreeLoading } = useQuery({
    queryKey: ['bom-explosion', selectedProduct],
    queryFn: async () => {
      const response = await apiClient.get(`/bom/${selectedProduct}/explosion`);
      return response.data as BOMComponent[];
    },
    enabled: !!selectedProduct
  });

  const toggleNode = (nodeId: number) => {
    setExpandedNodes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(nodeId)) {
        newSet.delete(nodeId);
      } else {
        newSet.add(nodeId);
      }
      return newSet;
    });
  };

  const expandAll = () => {
    if (bomTree) {
      const allIds = new Set<number>();
      const collectIds = (nodes: BOMComponent[]) => {
        nodes.forEach(node => {
          allIds.add(node.id);
          if (node.children) collectIds(node.children);
        });
      };
      collectIds(bomTree);
      setExpandedNodes(allIds);
    }
  };

  const collapseAll = () => {
    setExpandedNodes(new Set());
  };

  const filterTree = (nodes: BOMComponent[]): BOMComponent[] => {
    return nodes.filter(node => {
      const matchesSearch = searchTerm === '' || 
        node.component_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
        node.component_name.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesDepartment = departmentFilter === 'ALL' || 
        node.department === departmentFilter;

      return matchesSearch && matchesDepartment;
    }).map(node => ({
      ...node,
      children: node.children ? filterTree(node.children) : undefined
    }));
  };

  const renderNode = (node: BOMComponent, depth: number = 0) => {
    const hasChildren = node.children && node.children.length > 0;
    const isExpanded = expandedNodes.has(node.id);
    const indent = depth * 24;

    const getTypeColor = (type: string) => {
      switch (type) {
        case 'RAW': return 'bg-green-100 text-green-800';
        case 'WIP': return 'bg-blue-100 text-blue-800';
        case 'Finish Good': return 'bg-purple-100 text-purple-800';
        default: return 'bg-gray-100 text-gray-800';
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

    return (
      <div key={node.id}>
        <div
          className="flex items-center gap-2 py-2 px-3 hover:bg-gray-50 rounded-lg cursor-pointer"
          style={{ paddingLeft: `${indent + 12}px` }}
        >
          {/* Expand/Collapse Button */}
          <button
            onClick={() => hasChildren && toggleNode(node.id)}
            className={`flex-shrink-0 ${hasChildren ? 'text-gray-600' : 'text-transparent'}`}
          >
            {hasChildren && (
              isExpanded ? <ChevronDown size={18} /> : <ChevronRight size={18} />
            )}
            {!hasChildren && <div className="w-[18px]" />}
          </button>

          {/* Level Indicator */}
          <span className="flex-shrink-0 w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center text-xs font-bold text-gray-700">
            L{node.level}
          </span>

          {/* Type Icon */}
          <span className="text-xl flex-shrink-0">{getTypeIcon(node.component_type)}</span>

          {/* Component Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-gray-900">{node.component_code}</span>
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${getTypeColor(node.component_type)}`}>
                {node.component_type}
              </span>
              {node.department && (
                <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                  {node.department}
                </span>
              )}
            </div>
            <p className="text-sm text-gray-600 truncate">{node.component_name}</p>
          </div>

          {/* Quantity */}
          <div className="flex-shrink-0 text-right">
            <div className="font-bold text-gray-900">{node.quantity.toFixed(2)}</div>
            <div className="text-xs text-gray-600">{node.uom}</div>
          </div>
        </div>

        {/* Render Children */}
        {hasChildren && isExpanded && (
          <div>
            {node.children!.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  const filteredTree = bomTree ? filterTree(bomTree) : [];

  return (
    <div className="bg-white rounded-lg shadow-md">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center gap-3 mb-4">
          <div className="bg-blue-100 p-2 rounded-lg">
            <Boxes className="text-blue-600" size={24} />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900">BOM Explorer</h3>
            <p className="text-sm text-gray-600">Multi-level Bill of Materials</p>
          </div>
        </div>

        {/* Product Selector */}
        {showSearch && (
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Product
            </label>
            <select
              value={selectedProduct || ''}
              onChange={(e) => setSelectedProduct(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Choose a product...</option>
              {products?.map((p: any) => (
                <option key={p.id} value={p.id}>
                  [{p.code}] {p.name}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* BOM Header Info */}
        {bomHeader && (
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 mb-4">
            <div className="grid grid-cols-4 gap-4 text-sm">
              <div>
                <div className="text-gray-600">Product</div>
                <div className="font-bold text-gray-900">{bomHeader.product_code}</div>
              </div>
              <div>
                <div className="text-gray-600">Version</div>
                <div className="font-bold text-gray-900">{bomHeader.version}</div>
              </div>
              <div>
                <div className="text-gray-600">Status</div>
                <div className={`font-bold ${bomHeader.state === 'ACTIVE' ? 'text-green-600' : 'text-gray-600'}`}>
                  {bomHeader.state}
                </div>
              </div>
              <div>
                <div className="text-gray-600">Total Components</div>
                <div className="font-bold text-gray-900">{bomHeader.total_components}</div>
              </div>
            </div>
          </div>
        )}

        {/* Search & Filters */}
        {selectedProduct && (
          <div className="grid grid-cols-2 gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search components..."
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              />
            </div>

            <select
              value={departmentFilter}
              onChange={(e) => setDepartmentFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            >
              <option value="ALL">All Departments</option>
              <option value="CUTTING">Cutting</option>
              <option value="EMBROIDERY">Embroidery</option>
              <option value="SEWING">Sewing</option>
              <option value="FINISHING">Finishing</option>
              <option value="PACKING">Packing</option>
            </select>
          </div>
        )}

        {/* Expand/Collapse Controls */}
        {selectedProduct && filteredTree.length > 0 && (
          <div className="flex gap-2 mt-3">
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
        )}
      </div>

      {/* BOM Tree */}
      <div className="p-6">
        {!selectedProduct ? (
          <div className="text-center py-12">
            <Package className="mx-auto text-gray-400 mb-4" size={64} />
            <h4 className="text-lg font-semibold text-gray-900 mb-2">No Product Selected</h4>
            <p className="text-gray-600">Select a product to view its BOM structure</p>
          </div>
        ) : bomTreeLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading BOM tree...</p>
          </div>
        ) : filteredTree.length === 0 ? (
          <div className="text-center py-12">
            <Info className="mx-auto text-gray-400 mb-4" size={64} />
            <h4 className="text-lg font-semibold text-gray-900 mb-2">No Components Found</h4>
            <p className="text-gray-600">Try adjusting your search or filters</p>
          </div>
        ) : (
          <div className="space-y-1">
            {filteredTree.map(node => renderNode(node, 0))}
          </div>
        )}
      </div>

      {/* Footer Summary */}
      {selectedProduct && filteredTree.length > 0 && (
        <div className="px-6 py-3 bg-gray-50 border-t rounded-b-lg flex items-center justify-between text-sm text-gray-600">
          <span>Showing {filteredTree.length} top-level component(s)</span>
          <span>Total unique items: {bomHeader?.total_components || 0}</span>
        </div>
      )}
    </div>
  );
};
