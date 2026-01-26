/**
 * Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved
 * File: KanbanPage.tsx | Author: Daniel Rizaldy | Date: 2026-01-19
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { 
  FileText, 
  Clock,
  CheckCircle,
  Truck,
  Ban,
  AlertCircle,
  Filter
} from 'lucide-react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface KanbanCard {
  id: number;
  card_number: string;
  department: string;
  item_code: string;
  qty_per_card: number;
  status: string;
  priority: number;
  created_at: string;
  approved_at?: string;
  shipped_at?: string;
  received_at?: string;
}

const statusColumns = [
  { key: 'Requested', label: 'Requested', color: 'yellow', icon: Clock },
  { key: 'Approved', label: 'Approved', color: 'blue', icon: CheckCircle },
  { key: 'In Transit', label: 'In Transit', color: 'purple', icon: Truck },
  { key: 'Received', label: 'Received', color: 'green', icon: CheckCircle },
];

export default function KanbanPage() {
  const [selectedDept, setSelectedDept] = useState<string>('All');
  const [showRejected, setShowRejected] = useState(false);
  const queryClient = useQueryClient();

  const { data: kanbanCards, isLoading } = useQuery({
    queryKey: ['all-kanban-cards'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE}/ppic/kanban/cards/all`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    },
    refetchInterval: 3000
  });

  const approveCard = useMutation({
    mutationFn: async (cardId: number) => {
      const token = localStorage.getItem('access_token');
      return axios.post(`${API_BASE}/ppic/kanban/cards/${cardId}/approve`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-kanban-cards'] });
    }
  });

  const rejectCard = useMutation({
    mutationFn: async (data: { cardId: number; reason: string }) => {
      const token = localStorage.getItem('access_token');
      return axios.post(`${API_BASE}/ppic/kanban/cards/${data.cardId}/reject`, {
        reason: data.reason
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-kanban-cards'] });
    }
  });

  const shipCard = useMutation({
    mutationFn: async (cardId: number) => {
      const token = localStorage.getItem('access_token');
      return axios.post(`${API_BASE}/ppic/kanban/cards/${cardId}/ship`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-kanban-cards'] });
    }
  });

  const receiveCard = useMutation({
    mutationFn: async (cardId: number) => {
      const token = localStorage.getItem('access_token');
      return axios.post(`${API_BASE}/ppic/kanban/cards/${cardId}/receive`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-kanban-cards'] });
    }
  });

  const filterCards = (cards: KanbanCard[], status: string) => {
    if (!cards) return [];
    let filtered = cards.filter((card: KanbanCard) => card.status === status);
    if (selectedDept !== 'All') {
      filtered = filtered.filter((card: KanbanCard) => card.department === selectedDept);
    }
    return filtered.sort((a, b) => b.priority - a.priority);
  };

  const getRejectedCards = () => {
    if (!kanbanCards) return [];
    let rejected = kanbanCards.filter((card: KanbanCard) => card.status === 'Rejected');
    if (selectedDept !== 'All') {
      rejected = rejected.filter((card: KanbanCard) => card.department === selectedDept);
    }
    return rejected;
  };

  const departments = ['All', 'Cutting', 'Sewing', 'Finishing', 'Packing'];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <FileText className="w-8 h-8 mr-3 text-blue-600" />
              E-Kanban Board
            </h1>
            <p className="text-gray-500 mt-1">
              Visual management system for accessory requests
            </p>
          </div>
          
          {/* Department Filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-500" />
            <select
              value={selectedDept}
              onChange={(e) => setSelectedDept(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {departments.map(dept => (
                <option key={dept} value={dept}>{dept}</option>
              ))}
            </select>
            <button
              onClick={() => setShowRejected(!showRejected)}
              className={`px-4 py-2 rounded-lg transition ${
                showRejected 
                  ? 'bg-red-600 text-white' 
                  : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              Rejected ({getRejectedCards().length})
            </button>
          </div>
        </div>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {statusColumns.map(col => {
          const count = filterCards(kanbanCards || [], col.key).length;
          const Icon = col.icon;
          return (
            <div key={col.key} className={`bg-white rounded-lg shadow p-4 border-l-4 border-${col.color}-500`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{col.label}</p>
                  <p className="text-2xl font-bold text-gray-900">{count}</p>
                </div>
                <Icon className={`w-8 h-8 text-${col.color}-600`} />
              </div>
            </div>
          );
        })}
      </div>

      {/* Kanban Board */}
      {!showRejected ? (
        <div className="grid grid-cols-4 gap-4">
          {statusColumns.map(column => {
            const cards = filterCards(kanbanCards || [], column.key);
            const Icon = column.icon;
            
            return (
              <div key={column.key} className="bg-gray-100 rounded-lg p-4">
                <div className="flex items-center mb-4">
                  <Icon className={`w-5 h-5 text-${column.color}-600 mr-2`} />
                  <h3 className="font-semibold text-gray-900">{column.label}</h3>
                  <span className="ml-auto bg-gray-200 text-gray-700 px-2 py-1 rounded-full text-xs font-medium">
                    {cards.length}
                  </span>
                </div>

                <div className="space-y-3 max-h-[calc(100vh-320px)] overflow-y-auto">
                  {cards.map((card: KanbanCard) => (
                    <div 
                      key={card.id} 
                      className={`bg-white rounded-lg shadow p-4 hover:shadow-md transition ${
                        card.priority === 1 ? 'border-2 border-red-500' : ''
                      }`}
                    >
                      {/* Card Header */}
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-mono text-gray-500">{card.card_number}</span>
                        {card.priority === 1 && (
                          <AlertCircle className="w-4 h-4 text-red-600" />
                        )}
                      </div>

                      {/* Card Content */}
                      <div className="mb-3">
                        <h4 className="font-semibold text-gray-900 mb-1">{card.item_code}</h4>
                        <p className="text-sm text-gray-600">Qty: {card.qty_per_card} units</p>
                        <p className="text-xs text-gray-500 mt-1">{card.department}</p>
                      </div>

                      {/* Timeline */}
                      <div className="text-xs text-gray-500 space-y-1 mb-3">
                        <div className="flex items-center">
                          <Clock className="w-3 h-3 mr-1" />
                          Created: {format(new Date(card.created_at), 'dd MMM HH:mm')}
                        </div>
                        {card.approved_at && (
                          <div className="flex items-center text-blue-600">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            Approved: {format(new Date(card.approved_at), 'dd MMM HH:mm')}
                          </div>
                        )}
                        {card.shipped_at && (
                          <div className="flex items-center text-purple-600">
                            <Truck className="w-3 h-3 mr-1" />
                            Shipped: {format(new Date(card.shipped_at), 'dd MMM HH:mm')}
                          </div>
                        )}
                        {card.received_at && (
                          <div className="flex items-center text-green-600">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            Received: {format(new Date(card.received_at), 'dd MMM HH:mm')}
                          </div>
                        )}
                      </div>

                      {/* Actions */}
                      <div className="flex gap-2">
                        {card.status === 'Requested' && (
                          <>
                            <button
                              onClick={() => approveCard.mutate(card.id)}
                              disabled={approveCard.isPending}
                              className="flex-1 bg-blue-600 text-white px-3 py-1.5 rounded text-xs hover:bg-blue-700 transition disabled:opacity-50"
                            >
                              Approve
                            </button>
                            <button
                              onClick={() => {
                                const reason = prompt('Rejection reason:');
                                if (reason) {
                                  rejectCard.mutate({ cardId: card.id, reason });
                                }
                              }}
                              className="flex-1 bg-red-600 text-white px-3 py-1.5 rounded text-xs hover:bg-red-700 transition"
                            >
                              Reject
                            </button>
                          </>
                        )}

                        {card.status === 'Approved' && (
                          <button
                            onClick={() => shipCard.mutate(card.id)}
                            disabled={shipCard.isPending}
                            className="w-full bg-purple-600 text-white px-3 py-1.5 rounded text-xs hover:bg-purple-700 transition disabled:opacity-50"
                          >
                            Ship Now
                          </button>
                        )}

                        {card.status === 'In Transit' && (
                          <button
                            onClick={() => receiveCard.mutate(card.id)}
                            disabled={receiveCard.isPending}
                            className="w-full bg-green-600 text-white px-3 py-1.5 rounded text-xs hover:bg-green-700 transition disabled:opacity-50"
                          >
                            Confirm Received
                          </button>
                        )}

                        {card.status === 'Received' && (
                          <div className="w-full text-center text-xs text-green-600 font-medium">
                            ✓ Completed
                          </div>
                        )}
                      </div>
                    </div>
                  ))}

                  {cards.length === 0 && (
                    <div className="text-center py-8 text-gray-400 text-sm">
                      No cards in this column
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* Rejected Cards View */
        <div className="bg-white rounded-lg shadow">
          <div className="p-6">
            <div className="flex items-center mb-4">
              <Ban className="w-6 h-6 text-red-600 mr-2" />
              <h3 className="text-xl font-semibold text-gray-900">Rejected Cards</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {getRejectedCards().map((card: KanbanCard) => (
                <div key={card.id} className="border-2 border-red-200 rounded-lg p-4 bg-red-50">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-mono text-gray-600">{card.card_number}</span>
                    <Ban className="w-4 h-4 text-red-600" />
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-1">{card.item_code}</h4>
                  <p className="text-sm text-gray-600 mb-2">Qty: {card.qty_per_card} units</p>
                  <p className="text-xs text-gray-500">{card.department}</p>
                  <div className="mt-3 text-xs text-red-700">
                    Rejected: {format(new Date(card.created_at), 'dd MMM yyyy HH:mm')}
                  </div>
                </div>
              ))}

              {getRejectedCards().length === 0 && (
                <div className="col-span-3 text-center py-12 text-gray-400">
                  No rejected cards
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
