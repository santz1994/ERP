/**
 * PermissionManagementPage - User Permission Management
 * Created: 2026-01-21 | Phase 16 Week 4 | PBAC Integration
 * Purpose: View and manage user permissions (role-based + custom)
 */

import React, { useState, useEffect } from 'react'
import { Shield, Search, Users, Lock, X, Calendar, CheckCircle, AlertCircle } from 'lucide-react'
import { apiClient } from '@/api'
import { usePermission } from '@/hooks/usePermission'

interface User {
  id: number
  username: string
  email: string
  role: string
  department: string
  is_active: boolean
  created_at: string
}

interface Permission {
  id: number
  code: string
  name: string
  description: string
  module: string
  category: string
}

interface EffectivePermission {
  permission_code: string
  source: 'role' | 'custom'
  granted_by: string | null
  expires_at: string | null
}

interface UserPermissions {
  user: User
  role_permissions: string[]
  custom_permissions: Array<{
    permission_code: string
    granted_by_username: string
    granted_at: string
    expires_at: string | null
  }>
  effective_permissions: EffectivePermission[]
}

const PermissionManagementPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([])
  const [permissions, setPermissions] = useState<Permission[]>([])
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [userPermissions, setUserPermissions] = useState<UserPermissions | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [loading, setLoading] = useState(false)
  const [showGrantModal, setShowGrantModal] = useState(false)
  const [selectedPermission, setSelectedPermission] = useState('')
  const [expirationDate, setExpirationDate] = useState('')
  const [filterModule, setFilterModule] = useState<string>('all')

  // Permission checks
  const canViewPermissions = usePermission('admin.view_system_info')
  const canManagePermissions = usePermission('admin.manage_users')

  // Fetch users
  useEffect(() => {
    fetchUsers()
    fetchPermissions()
  }, [])

  const fetchUsers = async () => {
    try {
      setLoading(true)
      const response = await apiClient.get('/admin/users')
      // Defensive: Ensure response.data is array before filtering
      const userData = Array.isArray(response.data) ? response.data : []
      setUsers(userData.filter((u: User) => u.is_active))
    } catch (error) {
      console.error('Error fetching users:', error)
      // Set to empty array on error
      setUsers([])
    } finally {
      setLoading(false)
    }
  }

  const fetchPermissions = async () => {
    try {
      const response = await apiClient.get('/admin/permissions')
      // Defensive: Check if response.data exists
      if (!response.data) {
        setPermissions([])
        return
      }
      
      // Handle both array and object response formats
      if (Array.isArray(response.data)) {
        setPermissions(response.data)
      } else if (response.data.modules && Array.isArray(response.data.modules)) {
        // Convert modules format to flat permission array
        const flatPermissions: Permission[] = []
        response.data.modules.forEach((module: any) => {
          if (module?.permissions && Array.isArray(module.permissions)) {
            module.permissions.forEach((perm: string, index: number) => {
              flatPermissions.push({
                id: flatPermissions.length + 1,
                code: `${module.name}.${perm}`,
                name: perm,
                description: `${perm} permission for ${module.name}`,
                module: module.name,
                category: 'system'
              })
            })
          }
        })
        setPermissions(flatPermissions)
      } else if (response.data.permissions && Array.isArray(response.data.permissions)) {
        setPermissions(response.data.permissions)
      } else {
        // Fallback - set empty array
        setPermissions([])
      }
    } catch (error) {
      console.error('Error fetching permissions:', error)
      setPermissions([])
    }
  }

  const fetchUserPermissions = async (userId: number) => {
    try {
      setLoading(true)
      const response = await apiClient.get(`/admin/users/${userId}/permissions`)
      setUserPermissions(response.data)
    } catch (error) {
      console.error('Error fetching user permissions:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSelectUser = (user: User) => {
    setSelectedUser(user)
    fetchUserPermissions(user.id)
  }

  const handleGrantPermission = async () => {
    if (!selectedUser || !selectedPermission) return

    try {
      await apiClient.post(`/admin/users/${selectedUser.id}/permissions`, {
        permission_code: selectedPermission,
        expires_at: expirationDate || null
      })
      
      alert('Permission granted successfully')
      fetchUserPermissions(selectedUser.id)
      setShowGrantModal(false)
      setSelectedPermission('')
      setExpirationDate('')
    } catch (error) {
      console.error('Error granting permission:', error)
      alert('Failed to grant permission')
    }
  }

  const handleRevokePermission = async (permissionCode: string) => {
    if (!selectedUser) return
    if (!confirm(`Revoke permission "${permissionCode}"?`)) return

    try {
      await apiClient.delete(`/admin/users/${selectedUser.id}/permissions/${permissionCode}`)
      alert('Permission revoked successfully')
      fetchUserPermissions(selectedUser.id)
    } catch (error) {
      console.error('Error revoking permission:', error)
      alert('Failed to revoke permission')
    }
  }

  // Filter permissions by module - with defensive checks
  const modules = permissions && Array.isArray(permissions) 
    ? Array.from(new Set(permissions.map(p => p.module))) 
    : []
  const filteredPermissions = (permissions && Array.isArray(permissions))
    ? (filterModule === 'all' 
      ? permissions 
      : permissions.filter(p => p.module === filterModule))
    : []

  // Defensive: Ensure role_permissions and custom_permissions are always arrays
  const rolePermissionsArray = Array.isArray(userPermissions?.role_permissions) 
    ? userPermissions.role_permissions 
    : []
  const customPermissionsArray = Array.isArray(userPermissions?.custom_permissions)
    ? userPermissions.custom_permissions
    : []
  const effectivePermissionsArray = Array.isArray(userPermissions?.effective_permissions)
    ? userPermissions.effective_permissions
    : []

  // Filter users by search term
  const filteredUsers = users.filter(u =>
    u.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.role.toLowerCase().includes(searchTerm.toLowerCase())
  )

  // Permission not granted check
  if (!canViewPermissions) {
    return (
      <div className="p-8 max-w-4xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 flex items-center">
          <Lock className="w-8 h-8 text-red-600 mr-4" />
          <div>
            <h2 className="text-lg font-semibold text-red-900">Access Denied</h2>
            <p className="text-red-700">You don't have permission to view user permissions.</p>
            <p className="text-sm text-red-600 mt-1">Required: admin.view_system_info</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <Shield className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">Permission Management</h1>
        </div>
        <p className="text-gray-600">View and manage user permissions across the system</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* User List */}
        <div className="lg:col-span-1 bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center gap-2 bg-gray-50 px-3 py-2 rounded-lg">
              <Search className="w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search users..."
                className="bg-transparent flex-1 outline-none text-sm"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div className="mt-2 text-sm text-gray-500">
              {filteredUsers.length} users
            </div>
          </div>

          <div className="overflow-y-auto max-h-[600px]">
            {filteredUsers.map((user) => (
              <div
                key={user.id}
                onClick={() => handleSelectUser(user)}
                className={`p-4 cursor-pointer border-b border-gray-100 hover:bg-blue-50 transition ${
                  selectedUser?.id === user.id ? 'bg-blue-50 border-l-4 border-l-blue-600' : ''
                }`}
              >
                <div className="font-medium text-gray-900">{user.username}</div>
                <div className="text-sm text-gray-600">{user.email}</div>
                <div className="flex gap-2 mt-1">
                  <span className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded">
                    {user.role}
                  </span>
                  <span className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded">
                    {user.department}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Permission Details */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-200">
          {selectedUser ? (
            <>
              {/* User Header */}
              <div className="p-6 border-b border-gray-200">
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{selectedUser.username}</h2>
                    <p className="text-gray-600">{selectedUser.email}</p>
                    <div className="flex gap-2 mt-2">
                      <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
                        {selectedUser.role}
                      </span>
                      <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                        {selectedUser.department}
                      </span>
                    </div>
                  </div>
                  {canManagePermissions && (
                    <button
                      onClick={() => setShowGrantModal(true)}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
                    >
                      + Grant Permission
                    </button>
                  )}
                </div>
              </div>

              {/* Permissions List */}
              {loading ? (
                <div className="p-8 text-center text-gray-500">Loading permissions...</div>
              ) : userPermissions ? (
                <div className="p-6">
                  {/* Statistics */}
                  <div className="grid grid-cols-3 gap-4 mb-6">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">
                        {effectivePermissionsArray.length}
                      </div>
                      <div className="text-sm text-gray-600">Total Permissions</div>
                    </div>
                    <div className="bg-purple-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-purple-600">
                        {rolePermissionsArray.length}
                      </div>
                      <div className="text-sm text-gray-600">From Role</div>
                    </div>
                    <div className="bg-green-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">
                        {customPermissionsArray.length}
                      </div>
                      <div className="text-sm text-gray-600">Custom</div>
                    </div>
                  </div>

                  {/* Role Permissions */}
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <Shield className="w-5 h-5 text-purple-600" />
                      Role Permissions ({rolePermissionsArray.length})
                    </h3>
                    <div className="grid grid-cols-2 gap-2">
                      {rolePermissionsArray.map((perm) => (
                        <div
                          key={perm}
                          className="px-3 py-2 bg-purple-50 border border-purple-200 rounded-lg text-sm"
                        >
                          <code className="text-purple-700">{perm}</code>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Custom Permissions */}
                  {customPermissionsArray.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <CheckCircle className="w-5 h-5 text-green-600" />
                        Custom Permissions ({customPermissionsArray.length})
                      </h3>
                      <div className="space-y-3">
                        {customPermissionsArray.map((perm) => (
                          <div
                            key={perm.permission_code}
                            className="p-4 bg-green-50 border border-green-200 rounded-lg"
                          >
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <code className="text-green-700 font-medium">{perm.permission_code}</code>
                                <div className="text-sm text-gray-600 mt-1">
                                  Granted by: <span className="font-medium">{perm.granted_by_username}</span>
                                </div>
                                <div className="text-xs text-gray-500">
                                  {new Date(perm.granted_at).toLocaleString()}
                                </div>
                                {perm.expires_at && (
                                  <div className="flex items-center gap-1 mt-2 text-sm">
                                    <Calendar className="w-4 h-4 text-orange-600" />
                                    <span className="text-orange-600">
                                      Expires: {new Date(perm.expires_at).toLocaleDateString()}
                                    </span>
                                  </div>
                                )}
                              </div>
                              {canManagePermissions && (
                                <button
                                  onClick={() => handleRevokePermission(perm.permission_code)}
                                  className="text-red-600 hover:text-red-800"
                                >
                                  <X className="w-5 h-5" />
                                </button>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {userPermissions.custom_permissions.length === 0 && (
                    <div className="text-center text-gray-500 py-8">
                      <AlertCircle className="w-12 h-12 text-gray-300 mx-auto mb-2" />
                      <p>No custom permissions granted</p>
                    </div>
                  )}
                </div>
              ) : null}
            </>
          ) : (
            <div className="p-8 text-center text-gray-500">
              <Users className="w-16 h-16 text-gray-300 mx-auto mb-3" />
              <p className="text-lg">Select a user to view their permissions</p>
            </div>
          )}
        </div>
      </div>

      {/* Grant Permission Modal */}
      {showGrantModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">Grant Custom Permission</h2>
              <p className="text-sm text-gray-600 mt-1">
                Grant additional permission to {selectedUser?.username}
              </p>
            </div>

            <div className="p-6 overflow-y-auto max-h-[50vh]">
              {/* Module Filter */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Filter by Module
                </label>
                <select
                  value={filterModule}
                  onChange={(e) => setFilterModule(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="all">All Modules</option>
                  {modules.map(module => (
                    <option key={module} value={module}>{module}</option>
                  ))}
                </select>
              </div>

              {/* Permission Selection */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Permission
                </label>
                <select
                  value={selectedPermission}
                  onChange={(e) => setSelectedPermission(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="">-- Select a permission --</option>
                  {filteredPermissions.map((perm) => (
                    <option key={perm.code} value={perm.code}>
                      {perm.code} - {perm.name}
                    </option>
                  ))}
                </select>
                {selectedPermission && (
                  <div className="mt-2 p-3 bg-blue-50 rounded-lg text-sm text-gray-700">
                    {permissions.find(p => p.code === selectedPermission)?.description}
                  </div>
                )}
              </div>

              {/* Expiration Date */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Expiration Date (Optional)
                </label>
                <input
                  type="datetime-local"
                  value={expirationDate}
                  onChange={(e) => setExpirationDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Leave empty for permanent permission
                </p>
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowGrantModal(false)
                  setSelectedPermission('')
                  setExpirationDate('')
                }}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleGrantPermission}
                disabled={!selectedPermission}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Grant Permission
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default PermissionManagementPage
