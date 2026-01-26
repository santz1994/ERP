/**
 * AdminUserPage - User Management
 * Updated: 2026-01-21 | Phase 16 Week 4 | PBAC Integration
 */

import React, { useState, useEffect } from 'react'
import { Lock } from 'lucide-react'
import { apiClient } from '@/api/client'
import { usePermission } from '@/hooks/usePermission'

interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: string
  department?: string
  is_active: boolean
  created_at: string
  last_login?: string
}

const AdminUserPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [selectedUsers, setSelectedUsers] = useState<Set<number>>(new Set())
  
  // Permission checks (PBAC - Phase 16 Week 4)
  const canManageUsers = usePermission('admin.manage_users')
  const canViewSystemInfo = usePermission('admin.view_system_info')
  
  const [userForm, setUserForm] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
    role: 'Operator Cutting',
    department: 'Cutting'
  })

  const roles = [
    'Developer',
    'Superadmin',
    'Admin',
    'Manager',
    'Finance Manager',
    'PPIC Manager',
    'PPIC Admin',
    'SPV Cutting',
    'SPV Sewing',
    'SPV Finishing',
    'Operator Cutting',
    'Operator Embroidery',
    'Operator Sewing',
    'Operator Finishing',
    'Operator Packing',
    'QC Inspector',
    'QC Lab',
    'Warehouse Admin',
    'Warehouse Operator',
    'Purchasing',
    'Purchasing Head',
    'Security'
  ]

  const departments = [
    'PPIC',
    'Purchasing',
    'Warehouse',
    'Cutting',
    'Embroidery',
    'Sewing',
    'Finishing',
    'Packing',
    'Finishgoods',
    'QC',
    'Security',
    'Admin'
  ]

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/admin/users')
      setUsers(response.data)
    } catch (error) {
      console.error('Failed to fetch users:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await apiClient.post('/auth/register', userForm)
      setShowModal(false)
      resetForm()
      fetchUsers()
    } catch (error: any) {
      alert('Failed to create user: ' + error.response?.data?.detail)
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateUser = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingUser) return
    
    setLoading(true)
    try {
      await apiClient.put(`/admin/users/${editingUser.id}`, {
        full_name: userForm.full_name,
        email: userForm.email,
        role: userForm.role,
        department: userForm.department
      })
      setShowModal(false)
      setEditingUser(null)
      resetForm()
      fetchUsers()
    } catch (error: any) {
      alert('Failed to update user: ' + error.response?.data?.detail)
    } finally {
      setLoading(false)
    }
  }

  const handleDeactivateUser = async (userId: number) => {
    if (!confirm('Are you sure you want to deactivate this user?')) return
    
    setLoading(true)
    try {
      await apiClient.post(`/admin/users/${userId}/deactivate`)
      fetchUsers()
    } catch (error: any) {
      alert('Failed to deactivate user: ' + error.response?.data?.detail)
    } finally {
      setLoading(false)
    }
  }

  const handleReactivateUser = async (userId: number) => {
    setLoading(true)
    try {
      await apiClient.post(`/admin/users/${userId}/reactivate`)
      fetchUsers()
    } catch (error: any) {
      alert('Failed to reactivate user: ' + error.response?.data?.detail)
    } finally {
      setLoading(false)
    }
  }

  const handleResetPassword = async (userId: number) => {
    if (!confirm('Reset user password to default? User will be notified.')) return
    
    setLoading(true)
    try {
      await apiClient.post(`/admin/users/${userId}/reset-password`)
      alert('Password reset successfully')
    } catch (error: any) {
      alert('Failed to reset password: ' + error.response?.data?.detail)
    } finally {
      setLoading(false)
    }
  }

  const openEditModal = (user: User) => {
    setEditingUser(user)
    setUserForm({
      username: user.username,
      email: user.email,
      full_name: user.full_name,
      password: '',
      role: user.role,
      department: user.department || ''
    })
    setShowModal(true)
  }

  const openCreateModal = () => {
    setEditingUser(null)
    resetForm()
    setShowModal(true)
  }

  const resetForm = () => {
    setUserForm({
      username: '',
      email: '',
      full_name: '',
      password: '',
      role: 'Operator Cutting',
      department: 'Cutting'
    })
  }

  // Select functionality
  const toggleSelectUser = (userId: number) => {
    const newSelected = new Set(selectedUsers)
    if (newSelected.has(userId)) {
      newSelected.delete(userId)
    } else {
      newSelected.add(userId)
    }
    setSelectedUsers(newSelected)
  }

  const toggleSelectAll = () => {
    if (selectedUsers.size === users.length) {
      setSelectedUsers(new Set())
    } else {
      setSelectedUsers(new Set(users.map(u => u.id)))
    }
  }

  const bulkDeactivate = async () => {
    if (selectedUsers.size === 0) return
    if (!confirm(`Deactivate ${selectedUsers.size} user(s)?`)) return
    
    try {
      for (const userId of selectedUsers) {
        await apiClient.put(`/admin/users/${userId}`, { is_active: false })
      }
      setSelectedUsers(new Set())
      fetchUsers()
    } catch (error) {
      console.error('Error deactivating users:', error)
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
          <p className="text-gray-600 mt-1">Manage system users and permissions</p>
        </div>
        {canManageUsers ? (
          <button
            onClick={openCreateModal}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            + Create User
          </button>
        ) : (
          <div className="px-4 py-2 bg-gray-100 text-gray-500 rounded-lg flex items-center">
            <Lock className="w-4 h-4 mr-2" />
            Admin Only
          </div>
        )}
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg">
          <div className="text-sm opacity-90">Total Users</div>
          <div className="text-3xl font-bold mt-2">{users.length}</div>
        </div>
        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white shadow-lg">
          <div className="text-sm opacity-90">Active Users</div>
          <div className="text-3xl font-bold mt-2">{users.filter(u => u.is_active).length}</div>
        </div>
        <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-xl p-6 text-white shadow-lg">
          <div className="text-sm opacity-90">Inactive Users</div>
          <div className="text-3xl font-bold mt-2">{users.filter(u => !u.is_active).length}</div>
        </div>
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg">
          <div className="text-sm opacity-90">Operators</div>
          <div className="text-3xl font-bold mt-2">{users.filter(u => u.role.includes('Operator')).length}</div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {/* Bulk actions bar */}
        {selectedUsers.size > 0 && (
          <div className="bg-blue-50 border-b border-blue-200 px-6 py-3 flex justify-between items-center">
            <span className="text-sm font-medium text-blue-900">
              {selectedUsers.size} user(s) selected
            </span>
            <button
              onClick={bulkDeactivate}
              className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition"
            >
              Deactivate Selected
            </button>
          </div>
        )}
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedUsers.size === users.length && users.length > 0}
                    onChange={toggleSelectAll}
                    className="w-4 h-4 cursor-pointer"
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Department</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Login</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-8 text-center text-gray-500">
                    No users found.
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.id} className={`hover:bg-gray-50 ${selectedUsers.has(user.id) ? 'bg-blue-50' : ''}`}>
                    <td className="px-6 py-4">
                      <input
                        type="checkbox"
                        checked={selectedUsers.has(user.id)}
                        onChange={() => toggleSelectUser(user.id)}
                        className="w-4 h-4 cursor-pointer"
                      />
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <div className="font-medium text-gray-900">{user.full_name}</div>
                        <div className="text-sm text-gray-500">@{user.username}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">{user.email}</td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                        {user.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">{user.department || '-'}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <div className="flex gap-2">
                        {canManageUsers ? (
                          <>
                            <button
                              onClick={() => openEditModal(user)}
                              className="text-blue-600 hover:text-blue-800"
                            >
                              Edit
                            </button>
                            {user.is_active ? (
                              <button
                                onClick={() => handleDeactivateUser(user.id)}
                                className="text-red-600 hover:text-red-800"
                              >
                                Deactivate
                              </button>
                            ) : (
                              <button
                                onClick={() => handleReactivateUser(user.id)}
                                className="text-green-600 hover:text-green-800"
                              >
                                Reactivate
                              </button>
                            )}
                            <button
                              onClick={() => handleResetPassword(user.id)}
                              className="text-purple-600 hover:text-purple-800"
                            >
                              Reset Pwd
                            </button>
                          </>
                        ) : (
                          <span className="text-gray-400 text-sm flex items-center">
                            <Lock className="w-3 h-3 mr-1" />
                            View Only
                          </span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">
              {editingUser ? 'Edit User' : 'Create User'}
            </h2>
            <form onSubmit={editingUser ? handleUpdateUser : handleCreateUser} className="space-y-4">
              {!editingUser && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Username *</label>
                    <input
                      type="text"
                      value={userForm.username}
                      onChange={(e) => setUserForm({...userForm, username: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Password *</label>
                    <input
                      type="password"
                      value={userForm.password}
                      onChange={(e) => setUserForm({...userForm, password: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                      minLength={8}
                    />
                    <p className="text-xs text-gray-500 mt-1">Minimum 8 characters</p>
                  </div>
                </>
              )}
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name *</label>
                <input
                  type="text"
                  value={userForm.full_name}
                  onChange={(e) => setUserForm({...userForm, full_name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
                <input
                  type="email"
                  value={userForm.email}
                  onChange={(e) => setUserForm({...userForm, email: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Role *</label>
                <select
                  value={userForm.role}
                  onChange={(e) => setUserForm({...userForm, role: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {roles.map(role => (
                    <option key={role} value={role}>{role}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
                <select
                  value={userForm.department}
                  onChange={(e) => setUserForm({...userForm, department: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Department</option>
                  {departments.map(dept => (
                    <option key={dept} value={dept}>{dept}</option>
                  ))}
                </select>
              </div>
              
              <div className="flex justify-end gap-2 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false)
                    setEditingUser(null)
                    resetForm()
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
                >
                  {loading ? 'Saving...' : editingUser ? 'Update User' : 'Create User'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default AdminUserPage
