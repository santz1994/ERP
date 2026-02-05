/**
 * Security Settings Page (SUPERADMIN/DEVELOPER only)
 * Configure security policies and authentication options
 */

import React, { useState, useEffect } from 'react'
import { Lock, Save } from 'lucide-react'
import { useUIStore } from '@/store'

interface SecuritySettings {
  enableTwoFA: boolean
  enableBiometric: boolean
  enableIPWhitelist: boolean
  sessionTimeout: number
  passwordMinLength: number
  passwordRequireNumbers: boolean
  passwordRequireSymbols: boolean
  passwordRequireUppercase: boolean
  enableAPIKeys: boolean
  apiKeyExpiry: number
  enableWebhooks: boolean
  dataEncryption: boolean
}

export const SecuritySettings: React.FC = () => {
  const { addNotification } = useUIStore()
  const [loading, setLoading] = useState(false)
  const [settings, setSettings] = useState<SecuritySettings>({
    enableTwoFA: false,
    enableBiometric: false,
    enableIPWhitelist: false,
    sessionTimeout: 30,
    passwordMinLength: 8,
    passwordRequireNumbers: true,
    passwordRequireSymbols: true,
    passwordRequireUppercase: true,
    enableAPIKeys: false,
    apiKeyExpiry: 365,
    enableWebhooks: false,
    dataEncryption: true,
  })

  useEffect(() => {
    const saved = localStorage.getItem('securitySettings')
    if (saved) setSettings(JSON.parse(saved))
  }, [])

  const handleSave = async () => {
    try {
      setLoading(true)
      const settingsToSave = {
        ...settings,
        savedAt: new Date().toISOString()
      }
      localStorage.setItem('securitySettings', JSON.stringify(settingsToSave))
      await new Promise(resolve => setTimeout(resolve, 500))
      addNotification('success', 'Security settings saved successfully!')
    } catch (error) {
      addNotification('error', 'Failed to save settings')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-3xl">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Lock className="w-8 h-8 text-red-600" />
          <h1 className="text-3xl font-bold text-gray-900">Security Settings</h1>
        </div>
        <p className="text-gray-600">Configure authentication, access control, and data security options</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
        {/* Authentication */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b">Authentication & Access</h2>
          
          <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer mb-3">
            <input 
              type="checkbox" 
              checked={settings.enableTwoFA}
              onChange={() => setSettings(prev => ({ ...prev, enableTwoFA: !prev.enableTwoFA }))}
              className="w-4 h-4"
            />
            <div>
              <p className="font-medium">Two-Factor Authentication (2FA)</p>\n              <p className="text-xs text-gray-600\">Require 2FA for all user accounts</p>
            </div>
          </label>

          <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer mb-3">
            <input 
              type="checkbox" 
              checked={settings.enableBiometric}
              onChange={() => setSettings(prev => ({ ...prev, enableBiometric: !prev.enableBiometric }))}
              className="w-4 h-4"
            />
            <div>
              <p className="font-medium">Biometric Authentication</p>
              <p className="text-xs text-gray-600">Allow fingerprint/face recognition login</p>
            </div>
          </label>

          <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
            <input 
              type="checkbox" 
              checked={settings.enableIPWhitelist}
              onChange={() => setSettings(prev => ({ ...prev, enableIPWhitelist: !prev.enableIPWhitelist }))}
              className="w-4 h-4"
            />
            <div>
              <p className="font-medium\">IP Whitelist</p>
              <p className="text-xs text-gray-600\">Restrict access to specific IP addresses</p>
            </div>
          </label>

          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <label className="block text-sm font-medium text-gray-700 mb-2">Session Timeout (minutes)</label>
            <input 
              type="number" 
              value={settings.sessionTimeout}
              onChange={(e) => setSettings(prev => ({ ...prev, sessionTimeout: parseInt(e.target.value) }))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Password Policy */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b\">Password Policy</h2>
          
          <div className="p-3 bg-gray-50 rounded-lg mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2\">Minimum Password Length</label>
            <input 
              type="number" 
              value={settings.passwordMinLength}
              onChange={(e) => setSettings(prev => ({ ...prev, passwordMinLength: parseInt(e.target.value) }))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer mb-2">
            <input 
              type="checkbox" 
              checked={settings.passwordRequireNumbers}
              onChange={() => setSettings(prev => ({ ...prev, passwordRequireNumbers: !prev.passwordRequireNumbers }))}
              className="w-4 h-4"
            />
            <span className="text-sm font-medium">Require Numbers (0-9)</span>
          </label>

          <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer mb-2">
            <input 
              type="checkbox" 
              checked={settings.passwordRequireSymbols}
              onChange={() => setSettings(prev => ({ ...prev, passwordRequireSymbols: !prev.passwordRequireSymbols }))}
              className="w-4 h-4"
            />
            <span className="text-sm font-medium">Require Symbols (!@#$%^&*)</span>
          </label>

          <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
            <input 
              type="checkbox" 
              checked={settings.passwordRequireUppercase}
              onChange={() => setSettings(prev => ({ ...prev, passwordRequireUppercase: !prev.passwordRequireUppercase }))}
              className="w-4 h-4"
            />
            <span className="text-sm font-medium">Require Uppercase Letters (A-Z)</span>
          </label>
        </div>

        {/* API & Integration */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b">API & Integration</h2>
          
          <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer mb-3">
            <input 
              type="checkbox" 
              checked={settings.enableAPIKeys}
              onChange={() => setSettings(prev => ({ ...prev, enableAPIKeys: !prev.enableAPIKeys }))}
              className="w-4 h-4"
            />
            <div>
              <p className="font-medium">Enable API Keys</p>
              <p className="text-xs text-gray-600">Allow programmatic API access</p>
            </div>
          </label>

          {settings.enableAPIKeys && (
            <div className="p-3 bg-gray-50 rounded-lg mb-3">
              <label className="block text-sm font-medium text-gray-700 mb-2">API Key Expiry (days)</label>
              <input 
                type="number" 
                value={settings.apiKeyExpiry}
                onChange={(e) => setSettings(prev => ({ ...prev, apiKeyExpiry: parseInt(e.target.value) }))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          )}

          <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
            <input 
              type="checkbox" 
              checked={settings.enableWebhooks}
              onChange={() => setSettings(prev => ({ ...prev, enableWebhooks: !prev.enableWebhooks }))}
              className="w-4 h-4"
            />
            <div>
              <p className="font-medium">Enable Webhooks</p>
              <p className="text-xs text-gray-600">Allow external system integration via webhooks</p>
            </div>
          </label>
        </div>

        {/* Data Protection */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b">Data Protection</h2>
          
          <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
            <input 
              type="checkbox" 
              checked={settings.dataEncryption}
              onChange={() => setSettings(prev => ({ ...prev, dataEncryption: !prev.dataEncryption }))}
              className="w-4 h-4"
            />
            <div>
              <p className="font-medium">Data Encryption</p>
              <p className="text-xs text-gray-600">Encrypt sensitive data at rest and in transit</p>
            </div>
          </label>
        </div>

        <button 
          onClick={handleSave} 
          disabled={loading} 
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition"
        >
          <Save size={18} /> {loading ? 'Saving...' : 'Save Security Settings'}
        </button>
      </div>
    </div>
  )
}
