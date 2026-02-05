/**
 * Database Management Settings Page (DEVELOPER only)
 * Database maintenance, backups, and administration tools
 */

import React, { useState, useEffect } from 'react'
import { Database, Save, Download, RefreshCw, Copy, Trash2, Plus, Check, Lock } from 'lucide-react'
import { useUIStore } from '@/store'
import { usePermission } from '@/hooks/usePermission'

interface DatabaseSettings {
  autoBackupEnabled: boolean
  backupFrequency: 'daily' | 'weekly' | 'monthly'
  backupRetentionDays: number
  enableQueryLog: boolean
  queryLogRetentionDays: number
  enableConnectionPooling: boolean
  maxConnections: number
  maintenanceWindowDay: string
  maintenanceWindowHour: number
}

interface Database {
  id: string
  name: string
  size: string
  created: string
  status: 'active' | 'backup' | 'clone' | 'archive'
}

export const DatabaseManagementSettings: React.FC = () => {
  const { addNotification } = useUIStore()
  const [loading, setLoading] = useState(false)
  const [backupLoading, setBackupLoading] = useState(false)
  
  // Check if user has developer permission
  const isDeveloper = usePermission('admin.manage_system')
  
  if (!isDeveloper) {
    return (
      <div className="p-6 max-w-2xl">
        <div className="flex items-center gap-4">
          <Lock className="w-12 h-12 text-red-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Access Denied</h1>
            <p className="text-gray-600 mt-1">Database Management is only available to DEVELOPER users</p>
          </div>
        </div>
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">
            You do not have the required permissions to access database management features. Contact your system administrator if you need access.
          </p>
        </div>
      </div>
    )
  }
  const [databases, setDatabases] = useState<Database[]>([
    { id: '1', name: 'erp_quty_karunia', size: '2.4 GB', created: '2026-01-01', status: 'active' },
    { id: '2', name: 'erp_quty_karunia_backup_20260120', size: '2.3 GB', created: '2026-01-20', status: 'backup' },
  ])
  const [selectedDatabase, setSelectedDatabase] = useState<string>('1')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newDatabaseName, setNewDatabaseName] = useState('')
  const [settings, setSettings] = useState<DatabaseSettings>({
    autoBackupEnabled: true,
    backupFrequency: 'daily',
    backupRetentionDays: 30,
    enableQueryLog: true,
    queryLogRetentionDays: 7,
    enableConnectionPooling: true,
    maxConnections: 100,
    maintenanceWindowDay: 'Sunday',
    maintenanceWindowHour: 2,
  })

  useEffect(() => {
    const saved = localStorage.getItem('databaseSettings')
    if (saved) setSettings(JSON.parse(saved))
  }, [])

  const handleSave = async () => {
    try {
      setLoading(true)
      const settingsToSave = {
        ...settings,
        savedAt: new Date().toISOString()
      }
      localStorage.setItem('databaseSettings', JSON.stringify(settingsToSave))
      await new Promise(resolve => setTimeout(resolve, 500))
      addNotification('success', 'Database settings saved successfully!')
    } catch (error) {
      addNotification('error', 'Failed to save settings')
    } finally {
      setLoading(false)
    }
  }

  // Database Management Functions
  const duplicateDatabase = async (dbId: string) => {
    const db = databases.find(d => d.id === dbId)
    if (!db) return
    
    const cloneName = `${db.name}_clone_${new Date().getTime()}`
    const newDb: Database = {
      id: String(databases.length + 1),
      name: cloneName,
      size: db.size,
      created: new Date().toISOString().split('T')[0],
      status: 'clone'
    }
    
    try {
      setLoading(true)
      await new Promise(resolve => setTimeout(resolve, 2000))
      setDatabases([...databases, newDb])
      addNotification('success', `Database duplicated as "${cloneName}"`)
    } catch (error) {
      addNotification('error', 'Failed to duplicate database')
    } finally {
      setLoading(false)
    }
  }

  const deleteDatabase = async (dbId: string) => {
    const db = databases.find(d => d.id === dbId)
    if (!db || db.status === 'active') {
      addNotification('error', 'Cannot delete active database')
      return
    }
    
    if (!confirm(`Delete database "${db.name}"? This action cannot be undone.`)) return
    
    try {
      setLoading(true)
      await new Promise(resolve => setTimeout(resolve, 1000))
      setDatabases(databases.filter(d => d.id !== dbId))
      addNotification('success', `Database "${db.name}" deleted`)
    } catch (error) {
      addNotification('error', 'Failed to delete database')
    } finally {
      setLoading(false)
    }
  }

  const addNewDatabase = async () => {
    if (!newDatabaseName.trim()) {
      addNotification('error', 'Please enter a database name')
      return
    }
    
    const newDb: Database = {
      id: String(databases.length + 1),
      name: newDatabaseName,
      size: '0 MB',
      created: new Date().toISOString().split('T')[0],
      status: 'archive'
    }
    
    try {
      setLoading(true)
      await new Promise(resolve => setTimeout(resolve, 1500))
      setDatabases([...databases, newDb])
      setNewDatabaseName('')
      setShowCreateModal(false)
      addNotification('success', `Database "${newDatabaseName}" created`)
    } catch (error) {
      addNotification('error', 'Failed to create database')
    } finally {
      setLoading(false)
    }
  }

  const switchDatabase = async (dbId: string) => {
    try {
      setLoading(true)
      await new Promise(resolve => setTimeout(resolve, 1000))
      setSelectedDatabase(dbId)
      const dbName = databases.find(d => d.id === dbId)?.name
      addNotification('success', `Switched to database "${dbName}"`)
    } catch (error) {
      addNotification('error', 'Failed to switch database')
    } finally {
      setLoading(false)
    }
  }

  const handleBackupNow = async () => {
    try {
      setBackupLoading(true)
      // Simulate backup process
      setTimeout(() => {
        addNotification('success', 'Database backup completed successfully')
        setBackupLoading(false)
      }, 2000)
    } catch (error) {
      addNotification('error', 'Backup failed')
      setBackupLoading(false)
    }
  }

  const handleOptimizeDatabase = async () => {
    try {
      addNotification('info', 'Database optimization started...')
      setTimeout(() => {
        addNotification('success', 'Database optimization completed')
      }, 3000)
    } catch (error) {
      addNotification('error', 'Optimization failed')
    }
  }

  return (
    <div className="p-6 max-w-4xl">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Database className="w-8 h-8 text-indigo-600" />
          <h1 className="text-3xl font-bold text-gray-900">Database Management</h1>
        </div>
        <p className="text-gray-600">⚠️ DEVELOPER ONLY - Manage database selection, cloning, and maintenance</p>
      </div>

      <div className="space-y-6">
        {/* Database Selection */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b">Select Database</h2>
          <div className="grid gap-3">
            {databases.map(db => (
              <div 
                key={db.id} 
                onClick={() => switchDatabase(db.id)}
                className={`p-4 rounded-lg border-2 cursor-pointer transition ${
                  selectedDatabase === db.id 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 bg-white hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <Database size={18} className={selectedDatabase === db.id ? 'text-blue-600' : 'text-gray-600'} />
                      <span className="font-medium text-gray-900">{db.name}</span>
                      {selectedDatabase === db.id && <Check size={18} className="text-blue-600 ml-auto" />}
                    </div>
                    <div className="text-sm text-gray-500 mt-1">
                      Status: <span className="capitalize font-medium">{db.status}</span> • Size: {db.size} • Created: {db.created}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Database Actions */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b">Database Actions</h2>
          <div className="grid grid-cols-2 gap-4">
            <button 
              onClick={() => {
                const selected = databases.find(d => d.id === selectedDatabase)
                if (selected && selected.status === 'active') {
                  duplicateDatabase(selectedDatabase)
                } else {
                  addNotification('error', 'Can only duplicate active database')
                }
              }}
              disabled={loading}
              className="flex items-center justify-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white rounded-lg transition"
            >
              <Copy size={18} /> Duplicate Database
            </button>
            
            <button 
              onClick={() => setShowCreateModal(true)}
              disabled={loading}
              className="flex items-center justify-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg transition"
            >
              <Plus size={18} /> Add New Database
            </button>
            
            <button 
              onClick={() => {
                const selected = databases.find(d => d.id === selectedDatabase)
                if (selected && selected.status !== 'active') {
                  deleteDatabase(selectedDatabase)
                } else {
                  addNotification('error', 'Cannot delete active database')
                }
              }}
              disabled={loading || databases.find(d => d.id === selectedDatabase)?.status === 'active'}
              className="flex items-center justify-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white rounded-lg transition"
            >
              <Trash2 size={18} /> Delete Database
            </button>

            <button 
              onClick={handleBackupNow}
              disabled={backupLoading}
              className="flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition"
            >
              <Download size={18} /> {backupLoading ? 'Backing up...' : 'Backup Now'}
            </button>
          </div>
        </div>

        {/* Settings */}
        <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b">Backup Settings</h2>
            {/* Auto Backup */}
            <div className="mb-4">
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.autoBackupEnabled}
                  onChange={(e) => setSettings({...settings, autoBackupEnabled: e.target.checked})}
                  className="w-4 h-4 rounded"
                />
                <span className="ml-3 text-gray-900 font-medium">Enable Automatic Backups</span>
              </label>
            </div>

            {settings.autoBackupEnabled && (
              <>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Backup Frequency</label>
                  <select 
                    value={settings.backupFrequency}
                    onChange={(e) => setSettings({...settings, backupFrequency: e.target.value as any})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Retention Days: {settings.backupRetentionDays}</label>
                  <input 
                    type="range" 
                    min="7" 
                    max="90" 
                    value={settings.backupRetentionDays}
                    onChange={(e) => setSettings({...settings, backupRetentionDays: parseInt(e.target.value)})}
                    className="w-full"
                  />
                </div>
              </>
            )}
          </div>

          <button 
            onClick={handleSave} 
            disabled={loading} 
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition"
          >
            <Save size={18} /> {loading ? 'Saving...' : 'Save Database Settings'}
          </button>
        </div>

        {/* Create Database Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Create New Database</h3>
              <input
                type="text"
                placeholder="Enter database name"
                value={newDatabaseName}
                onChange={(e) => setNewDatabaseName(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addNewDatabase()}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-4"
                autoFocus
              />
              <div className="flex gap-2">
                <button
                  onClick={addNewDatabase}
                  disabled={loading}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white py-2 rounded-lg transition"
                >
                  Create
                </button>
                <button
                  onClick={() => {
                    setShowCreateModal(false)
                    setNewDatabaseName('')
                  }}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-900 py-2 rounded-lg transition"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Information Box */}
        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            <strong>Warning:</strong> Database operations are developer-only features. Changes may require system restart. Always backup before making critical changes.
          </p>
        </div>
      </div>
    </div>
  )
}
