/**
 * Notifications Settings Page
 * Configure notification preferences and channels
 */

import React, { useState } from 'react'
import { Bell, Mail, MessageSquare, Save } from 'lucide-react'
import { useUIStore } from '@/store'

interface NotificationSettings {
  emailNotifications: boolean
  pushNotifications: boolean
  smsNotifications: boolean
  productionAlerts: boolean
  qualityAlerts: boolean
  inventoryAlerts: boolean
  systemNotifications: boolean
  digestFrequency: 'immediate' | 'hourly' | 'daily'
}

export const NotificationsSettings: React.FC = () => {
  const { addNotification } = useUIStore()
  const [loading, setLoading] = useState(false)
  const [settings, setSettings] = useState<NotificationSettings>({
    emailNotifications: true,
    pushNotifications: true,
    smsNotifications: false,
    productionAlerts: true,
    qualityAlerts: true,
    inventoryAlerts: true,
    systemNotifications: true,
    digestFrequency: 'immediate',
  })

  const handleToggle = (key: keyof NotificationSettings) => {
    setSettings(prev => ({
      ...prev,
      [key]: typeof prev[key] === 'boolean' ? !prev[key] : prev[key]
    }))
  }

  const handleSave = async () => {
    try {
      setLoading(true)
      localStorage.setItem('notificationSettings', JSON.stringify(settings))
      addNotification('success', 'Notification settings saved!')
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
          <Bell className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">Notifications</h1>
        </div>
        <p className="text-gray-600">Manage how you receive alerts and notifications</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
        {/* Notification Channels */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Notification Channels</h2>
          <div className="space-y-3">
            <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.emailNotifications}
                onChange={() => handleToggle('emailNotifications')}
                className="w-4 h-4"
              />
              <Mail className="w-5 h-5 text-gray-600" />
              <div>
                <p className="font-medium text-gray-900">Email Notifications</p>
                <p className="text-xs text-gray-600">Receive alerts via email</p>
              </div>
            </label>

            <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.pushNotifications}
                onChange={() => handleToggle('pushNotifications')}
                className="w-4 h-4"
              />
              <Bell className="w-5 h-5 text-gray-600" />
              <div>
                <p className="font-medium text-gray-900">Browser Notifications</p>
                <p className="text-xs text-gray-600">Real-time in-app alerts</p>
              </div>
            </label>

            <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer opacity-50">
              <input
                type="checkbox"
                checked={settings.smsNotifications}
                onChange={() => handleToggle('smsNotifications')}
                disabled
                className="w-4 h-4"
              />
              <MessageSquare className="w-5 h-5 text-gray-600" />
              <div>
                <p className="font-medium text-gray-900">SMS Notifications</p>
                <p className="text-xs text-gray-600">Critical alerts via SMS (Coming soon)</p>
              </div>
            </label>
          </div>
        </div>

        {/* Alert Types */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Alert Types</h2>
          <div className="space-y-3">
            <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.productionAlerts}
                onChange={() => handleToggle('productionAlerts')}
                className="w-4 h-4"
              />
              <div>
                <p className="font-medium text-gray-900">Production Alerts</p>
                <p className="text-xs text-gray-600">Work order status changes, delays</p>
              </div>
            </label>

            <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.qualityAlerts}
                onChange={() => handleToggle('qualityAlerts')}
                className="w-4 h-4"
              />
              <div>
                <p className="font-medium text-gray-900">Quality Alerts</p>
                <p className="text-xs text-gray-600">QC failures, inspections</p>
              </div>
            </label>

            <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.inventoryAlerts}
                onChange={() => handleToggle('inventoryAlerts')}
                className="w-4 h-4"
              />
              <div>
                <p className="font-medium text-gray-900">Inventory Alerts</p>
                <p className="text-xs text-gray-600">Low stock, transfers, movements</p>
              </div>
            </label>

            <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.systemNotifications}
                onChange={() => handleToggle('systemNotifications')}
                className="w-4 h-4"
              />
              <div>
                <p className="font-medium text-gray-900">System Notifications</p>
                <p className="text-xs text-gray-600">Maintenance, updates, important system messages</p>
              </div>
            </label>
          </div>
        </div>

        {/* Digest Frequency */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Notification Frequency
          </label>
          <div className="grid grid-cols-3 gap-2">
            {(['immediate', 'hourly', 'daily'] as const).map(freq => (
              <button
                key={freq}
                onClick={() => setSettings(prev => ({ ...prev, digestFrequency: freq }))}
                className={`p-3 rounded border-2 text-sm font-medium capitalize transition-colors ${
                  settings.digestFrequency === freq
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                {freq}
              </button>
            ))}
          </div>
        </div>

        {/* Save Button */}
        <button
          onClick={handleSave}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors"
        >
          <Save size={18} />
          {loading ? 'Saving...' : 'Save Settings'}
        </button>
      </div>
    </div>
  )
}
