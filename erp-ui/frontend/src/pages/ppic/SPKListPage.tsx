import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { 
  FileText, 
  Plus, 
  Search, 
  Filter,
  Calendar,
  AlertCircle,
  CheckCircle,
  Clock,
  TrendingUp,
  Eye
} from 'lucide-react';
import { apiClient } from '@/api';
import { getStatusBadge } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface SPK {
  id: number;
  spk_number: string;
  mo_id: number;
  mo_number: string;
  department: string;
  target_qty: number;
  actual_qty: number;
  good_output: number;
  rework_qty: number;
  reject_qty: number;
  status: string;
  start_date: string;
  target_date: string;
  completion_date?: string;
  article_code?: string;
  article_name?: string;
  po_label_number?: string;
}

interface SPKStats {
  total_active: number;
  completed_today: number;
  delayed: number;
  in_progress: number;
}

const SPKListPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [departmentFilter, setDepartmentFilter] = useState<string>('ALL');

  // Fetch SPK stats
  const { data: stats } = useQuery<SPKStats>({
    queryKey: ['spk-stats'],
    queryFn: async () => {
      const response = await apiClient.get('/production/spk/stats');
      return response.data;
    },
  });

  // Fetch SPKs list
  const { data: spks, isLoading, error } = useQuery<SPK[]>({
    queryKey: ['spks', searchTerm, statusFilter, departmentFilter],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (statusFilter !== 'ALL') params.append('status', statusFilter);
      if (departmentFilter !== 'ALL') params.append('department', departmentFilter);
      
      const response = await apiClient.get(`/production/spk?${params}`);
      return response.data;
    },
  });

  const filteredSPKs = spks || [];

  const calculateProgress = (spk: SPK) => {
    if (spk.target_qty === 0) return 0;
    return Math.round((spk.actual_qty / spk.target_qty) * 100);
  };

  const getProgressColor = (progress: number) => {
    if (progress >= 100) return 'text-green-600';
    if (progress >= 70) return 'text-blue-600';
    if (progress >= 30) return 'text-yellow-600';
    return 'text-red-600';
  };

  const isDelayed = (spk: SPK) => {
    if (spk.status === 'COMPLETED') return false;
    const today = new Date();
    const targetDate = new Date(spk.target_date);
    return today > targetDate;
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">SPK Management</h1>
          <p className="text-gray-500 mt-1">Manage work orders across all production departments</p>
        </div>
        <Link to="/ppic/spk/create">
          <Button className="gap-2">
            <Plus className="w-4 h-4" />
            Create SPK
          </Button>
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Active SPK</p>
                <p className="text-2xl font-bold text-blue-600">{stats?.total_active || 0}</p>
              </div>
              <FileText className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">In Progress</p>
                <p className="text-2xl font-bold text-yellow-600">{stats?.in_progress || 0}</p>
              </div>
              <Clock className="w-8 h-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Completed Today</p>
                <p className="text-2xl font-bold text-green-600">{stats?.completed_today || 0}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Delayed SPK</p>
                <p className="text-2xl font-bold text-red-600">{stats?.delayed || 0}</p>
              </div>
              <AlertCircle className="w-8 h-8 text-red-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative md:col-span-2">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Search by SPK number, MO, Article..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Filter by Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">All Status</SelectItem>
                <SelectItem value="DRAFT">Draft</SelectItem>
                <SelectItem value="RELEASED">Released</SelectItem>
                <SelectItem value="ONGOING">Ongoing</SelectItem>
                <SelectItem value="COMPLETED">Completed</SelectItem>
                <SelectItem value="CANCELLED">Cancelled</SelectItem>
              </SelectContent>
            </Select>

            <Select value={departmentFilter} onValueChange={setDepartmentFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Filter by Department" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">All Departments</SelectItem>
                <SelectItem value="CUTTING">Cutting</SelectItem>
                <SelectItem value="EMBROIDERY">Embroidery</SelectItem>
                <SelectItem value="SEWING">Sewing</SelectItem>
                <SelectItem value="FINISHING">Finishing</SelectItem>
                <SelectItem value="PACKING">Packing</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* SPK Table */}
      <Card>
        <CardHeader>
          <CardTitle>SPK List ({filteredSPKs.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-gray-500 mt-2">Loading SPKs...</p>
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-2" />
              <p className="text-red-600">Failed to load SPKs</p>
            </div>
          ) : filteredSPKs.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-500">No SPKs found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">SPK Number</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">MO Number</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Department</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Article</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Progress</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Target Date</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredSPKs.map((spk) => {
                    const progress = calculateProgress(spk);
                    const statusConfig = getStatusBadge(spk.status, 'spk');
                    const delayed = isDelayed(spk);

                    return (
                      <tr key={spk.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-gray-900">{spk.spk_number}</span>
                            {delayed && <AlertCircle className="w-4 h-4 text-red-500" />}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <Link 
                            to={`/ppic/mo/${spk.mo_id}`}
                            className="text-blue-600 hover:underline"
                          >
                            {spk.mo_number}
                          </Link>
                        </td>
                        <td className="px-4 py-3">
                          <Badge variant="outline">{spk.department}</Badge>
                        </td>
                        <td className="px-4 py-3">
                          <div>
                            <div className="font-medium text-gray-900">{spk.article_code || '-'}</div>
                            <div className="text-sm text-gray-500">{spk.article_name || '-'}</div>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <div>
                            <div className="flex items-center gap-2">
                              <div className="flex-1 bg-gray-200 rounded-full h-2">
                                <div
                                  className={`h-2 rounded-full transition-all ${
                                    progress >= 100 ? 'bg-green-500' :
                                    progress >= 70 ? 'bg-blue-500' :
                                    progress >= 30 ? 'bg-yellow-500' :
                                    'bg-red-500'
                                  }`}
                                  style={{ width: `${Math.min(progress, 100)}%` }}
                                />
                              </div>
                              <span className={`text-sm font-medium ${getProgressColor(progress)}`}>
                                {progress}%
                              </span>
                            </div>
                            <div className="text-xs text-gray-500 mt-1">
                              {spk.actual_qty.toLocaleString()} / {spk.target_qty.toLocaleString()} pcs
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="text-sm">
                            <div className="text-gray-900">
                              {new Date(spk.target_date).toLocaleDateString('id-ID')}
                            </div>
                            {delayed && (
                              <div className="text-red-600 text-xs">Delayed!</div>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <Badge variant={statusConfig.variant}>
                            {statusConfig.label}
                          </Badge>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex gap-2">
                            <Link to={`/ppic/spk/${spk.id}`}>
                              <Button variant="ghost" size="sm">
                                <Eye className="w-4 h-4" />
                              </Button>
                            </Link>
                            <Link to={`/production/calendar?spk=${spk.id}`}>
                              <Button variant="ghost" size="sm">
                                <Calendar className="w-4 h-4" />
                              </Button>
                            </Link>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default SPKListPage;
