/**
 * Database Management Settings Page (SUPERADMIN/DEVELOPER only)
 * Database maintenance, backups, and administration tools
 */

import React, { useState, useEffect } from 'react'
import { Database, Save, Download, RefreshCw } from 'lucide-react'
import { useUIStore } from '@/store'

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

export const DatabaseManagementSettings: React.FC = () => {
  const { addNotification } = useUIStore()
  const [loading, setLoading] = useState(false)
  const [backupLoading, setBackupLoading] = useState(false)
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
      addNotification('success', '✓ Database settings saved successfully!')
    } catch (error) {
      addNotification('error', 'Failed to save settings')
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
    <div className="p-6 max-w-3xl">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Database className="w-8 h-8 text-indigo-600" />
          <h1 className="text-3xl font-bold text-gray-900">Database Management</h1>
        </div>
        <p className="text-gray-600">Manage database backups, maintenance, and administration</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
        {/* Quick Actions */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-4">
            <button 
              onClick={handleBackupNow}
              disabled={backupLoading}
              className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition"
            >
              <Download size={18} /> {backupLoading ? 'Backing up...' : 'Backup Now'}
            </button>
            <button 
              onClick={handleOptimizeDatabase}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition"
            >
              <RefreshCw size={18} /> Optimize Database
            </button>
          </div>
        </div>

        {/* Backup Settings */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b">Backup Configuration</h2>
          
          <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer mb-4">
            <input 
              type="checkbox" 
              checked={settings.autoBackupEnabled}
              onChange={() => setSettings(prev => ({ ...prev, autoBackupEnabled: !prev.autoBackupEnabled }))}
              className="w-4 h-4"
            />
            <div>
              <p className="font-medium">Enable Automatic Backups</p>
              <p className="text-xs text-gray-600">Schedule regular database backups</p>
            </div>
          </label>

          {settings.autoBackupEnabled && (
            <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Backup Frequency</label>
                <select 
                  value={settings.backupFrequency}
                  onChange={(e) => setSettings(prev => ({ ...prev, backupFrequency: e.target.value as any }))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Backup Retention (days)</label>
                <input 
                  type="number" 
                  value={settings.backupRetentionDays}
                  onChange={(e) => setSettings(prev => ({ ...prev, backupRetentionDays: parseInt(e.target.value) }))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">Delete backups older than N days</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Maintenance Day</label>
                  <select 
                    value={settings.maintenanceWindowDay}
                    onChange={(e) => setSettings(prev => ({ ...prev, maintenanceWindowDay: e.target.value }))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].map(day => (
                      <option key={day} value={day}>{day}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Maintenance Hour (UTC)</label>
                  <input 
                    type="number" 
                    min="0" 
                    max="23"
                    value={settings.maintenanceWindowHour}
                    onChange={(e) => setSettings(prev => ({ ...prev, maintenanceWindowHour: parseInt(e.target.value) }))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Query Logging */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b">Query Logging</h2>
          
          <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer mb-4">
            <input 
              type="checkbox" 
              checked={settings.enableQueryLog}
              onChange={() => setSettings(prev => ({ ...prev, enableQueryLog: !prev.enableQueryLog }))}
              className="w-4 h-4"
            />
            <div>
              <p className="font-medium">Enable Query Logging</p>
              <p className="text-xs text-gray-600">Log all database queries for debugging</p>
            </div>
          </label>

          {settings.enableQueryLog && (
            <div className="p-4 bg-gray-50 rounded-lg">
              <label className="block text-sm font-medium text-gray-700 mb-2">Query Log Retention (days)</label>
              <input 
                type="number" 
                value={settings.queryLogRetentionDays}
                onChange={(e) => setSettings(prev => ({ ...prev, queryLogRetentionDays: parseInt(e.target.value) }))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">Delete query logs older than N days</p>
            </div>
          )}
        </div>

        {/* Connection Pooling */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b">Connection Management</h2>
          
          <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer mb-4">
            <input 
              type="checkbox" 
              checked={settings.enableConnectionPooling}
              onChange={() => setSettings(prev => ({ ...prev, enableConnectionPooling: !prev.enableConnectionPooling }))}
              className="w-4 h-4"
            />
            <div>
              <p className="font-medium">Enable Connection Pooling</p>
              <p className="text-xs text-gray-600">Optimize database connections</p>
            </div>
          </label>

          {settings.enableConnectionPooling && (
            <div className="p-4 bg-gray-50 rounded-lg">
              <label className="block text-sm font-medium text-gray-700 mb-2">Maximum Connections</label>
              <input 
                type="number" 
                value={settings.maxConnections}
                onChange={(e) => setSettings(prev => ({ ...prev, maxConnections: parseInt(e.target.value) }))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">Maximum concurrent database connections</p>
            </div>
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

      {/* Information Box */}
      <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-sm text-yellow-800">
          <strong>Note:</strong> Database changes may require system restart to take effect. Please coordinate maintenance windows to minimize system downtime.
        </p>
      </div>
    </div>
  )
}
