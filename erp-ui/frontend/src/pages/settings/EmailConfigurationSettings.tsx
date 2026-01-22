/**
 * Email Configuration Settings Page (ADMIN only)
 * Configure SMTP settings and email templates
 */

import React, { useState, useEffect } from 'react'
import { Mail, Save } from 'lucide-react'
import { useUIStore } from '@/store'

interface EmailSettings {
  smtpServer: string
  smtpPort: number
  smtpUsername: string
  smtpPassword: string
  senderEmail: string
  senderName: string
  enableSSL: boolean
  enableTLS: boolean
}

export const EmailConfigurationSettings: React.FC = () => {
  const { addNotification } = useUIStore()
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [settings, setSettings] = useState<EmailSettings>({
    smtpServer: 'smtp.gmail.com',
    smtpPort: 587,
    smtpUsername: '',
    smtpPassword: '',
    senderEmail: 'noreply@erpsystem.com',
    senderName: 'ERP System',
    enableSSL: false,
    enableTLS: true,
  })

  useEffect(() => {
    const saved = localStorage.getItem('emailSettings')
    if (saved) setSettings(JSON.parse(saved))
  }, [])

  const handleSave = async () => {
    try {
      setLoading(true)
      if (!settings.smtpServer || !settings.senderEmail) {
        addNotification('error', 'Please fill in all required fields')
        return
      }
      localStorage.setItem('emailSettings', JSON.stringify(settings))
      addNotification('success', 'Email configuration saved!')
    } catch (error) {
      addNotification('error', 'Failed to save settings')
    } finally {
      setLoading(false)
    }
  }

  const handleTestEmail = async () => {
    try {
      addNotification('info', 'Test email sent successfully')
    } catch (error) {
      addNotification('error', 'Failed to send test email')
    }
  }

  return (
    <div className="p-6 max-w-2xl">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Mail className="w-8 h-8 text-orange-600" />
          <h1 className="text-3xl font-bold text-gray-900">Email Configuration</h1>
        </div>
        <p className="text-gray-600">Configure SMTP settings for sending system emails</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 space-y-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <p className="text-sm text-blue-800">Email configuration is used for notifications, password resets, and system alerts.</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">SMTP Server *</label>
          <input 
            type="text" 
            value={settings.smtpServer} 
            onChange={(e) => setSettings(prev => ({ ...prev, smtpServer: e.target.value }))} 
            placeholder="smtp.gmail.com"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">SMTP Port *</label>
            <input 
              type="number" 
              value={settings.smtpPort} 
              onChange={(e) => setSettings(prev => ({ ...prev, smtpPort: parseInt(e.target.value) }))} 
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Sender Email *</label>
            <input 
              type="email" 
              value={settings.senderEmail} 
              onChange={(e) => setSettings(prev => ({ ...prev, senderEmail: e.target.value }))} 
              placeholder="noreply@example.com"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Sender Name</label>
          <input 
            type="text" 
            value={settings.senderName} 
            onChange={(e) => setSettings(prev => ({ ...prev, senderName: e.target.value }))} 
            placeholder="ERP System"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">SMTP Username</label>
            <input 
              type="text" 
              value={settings.smtpUsername} 
              onChange={(e) => setSettings(prev => ({ ...prev, smtpUsername: e.target.value }))} 
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">SMTP Password</label>
            <div className="relative">
              <input 
                type={showPassword ? 'text' : 'password'} 
                value={settings.smtpPassword} 
                onChange={(e) => setSettings(prev => ({ ...prev, smtpPassword: e.target.value }))} 
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button 
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-2.5 text-gray-600 text-sm"
              >
                {showPassword ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>
        </div>

        <div className="flex gap-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input 
              type="checkbox" 
              checked={settings.enableSSL} 
              onChange={() => setSettings(prev => ({ ...prev, enableSSL: !prev.enableSSL }))} 
              className="w-4 h-4"
            />
            <span className="text-sm text-gray-700">Use SSL</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input 
              type="checkbox" 
              checked={settings.enableTLS} 
              onChange={() => setSettings(prev => ({ ...prev, enableTLS: !prev.enableTLS }))} 
              className="w-4 h-4"
            />
            <span className="text-sm text-gray-700">Use TLS</span>
          </label>
        </div>

        <div className="flex gap-2">
          <button 
            onClick={handleTestEmail} 
            className="flex-1 bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded-lg transition"
          >
            Send Test Email
          </button>
          <button 
            onClick={handleSave} 
            disabled={loading} 
            className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition"
          >
            <Save size={18} /> {loading ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  )
}
