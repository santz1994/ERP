/**
 * Access Control Settings Page (SUPERADMIN/ADMIN only)
 * Manage system-wide access control policies
 */

import React, { useState, useEffect } from 'react'
import { Shield, Save } from 'lucide-react'
import { useUIStore } from '@/store'

interface AccessSettings {
  sessionTimeout: number
  requireMFA: boolean
  passwordExpiry: number
  loginAttempts: number
  ipWhitelist: boolean
  enableAudit: boolean
}

export const AccessControlSettings: React.FC = () => {
  const { addNotification } = useUIStore()
  const [loading, setLoading] = useState(false)
  const [settings, setSettings] = useState<AccessSettings>({
    sessionTimeout: 30,
    requireMFA: false,
    passwordExpiry: 90,
    loginAttempts: 5,
    ipWhitelist: false,
    enableAudit: true,
  })

  useEffect(() => {
    const saved = localStorage.getItem('accessSettings')
    if (saved) setSettings(JSON.parse(saved))
  }, [])

  const handleSave = async () => {
    try {
      setLoading(true)
      const settingsToSave = {
        ...settings,
        savedAt: new Date().toISOString()
      }
      localStorage.setItem('accessSettings', JSON.stringify(settingsToSave))
      await new Promise(resolve => setTimeout(resolve, 500))
      addNotification('success', 'Access control settings saved successfully!')
    } catch (error) {
      addNotification('error', 'Failed to save settings')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-2xl">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Shield className="w-8 h-8 text-red-600" />
          <h1 className="text-3xl font-bold text-gray-900">Access Control</h1>
        </div>
        <p className="text-gray-600">Manage system-wide access policies and security settings</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Session Timeout (minutes)</label>
          <input 
            type="number" 
            value={settings.sessionTimeout} 
            onChange={(e) => setSettings(prev => ({ ...prev, sessionTimeout: parseInt(e.target.value) }))} 
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p className="text-xs text-gray-500 mt-1">Automatically log out inactive users</p>
        </div>

        <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
          <input 
            type="checkbox" 
            checked={settings.requireMFA} 
            onChange={() => setSettings(prev => ({ ...prev, requireMFA: !prev.requireMFA }))} 
            className="w-4 h-4"
          />
          <div>
            <p className="font-medium">Require Multi-Factor Authentication</p>
            <p className="text-xs text-gray-600">All users must use MFA</p>
          </div>
        </label>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Password Expiry (days)</label>
          <input 
            type="number" 
            value={settings.passwordExpiry} 
            onChange={(e) => setSettings(prev => ({ ...prev, passwordExpiry: parseInt(e.target.value) }))} 
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p className="text-xs text-gray-500 mt-1">Force password change after N days</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Max Login Attempts Before Lockout</label>
          <input 
            type="number" 
            value={settings.loginAttempts} 
            onChange={(e) => setSettings(prev => ({ ...prev, loginAttempts: parseInt(e.target.value) }))} 
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p className="text-xs text-gray-500 mt-1">Lock account after N failed attempts</p>
        </div>

        <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
          <input 
            type="checkbox" 
            checked={settings.ipWhitelist} 
            onChange={() => setSettings(prev => ({ ...prev, ipWhitelist: !prev.ipWhitelist }))} 
            className="w-4 h-4"
          />
          <div>
            <p className="font-medium">IP Whitelist</p>
            <p className="text-xs text-gray-600">Restrict access to whitelisted IPs</p>
          </div>
        </label>

        <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
          <input 
            type="checkbox" 
            checked={settings.enableAudit} 
            onChange={() => setSettings(prev => ({ ...prev, enableAudit: !prev.enableAudit }))} 
            className="w-4 h-4"
          />
          <div>
            <p className="font-medium">Enable Audit Logging</p>
            <p className="text-xs text-gray-600">Log all user actions and changes</p>
          </div>
        </label>

        <button 
          onClick={handleSave} 
          disabled={loading} 
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition"
        >
          <Save size={18} /> {loading ? 'Saving...' : 'Save Settings'}
        </button>
      </div>
    </div>
  )
}
