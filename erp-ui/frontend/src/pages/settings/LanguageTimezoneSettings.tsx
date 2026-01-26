/**
 * Language & Timezone Settings Page
 * Allows users to set language preferences and timezone
 */

import React, { useState, useEffect } from 'react'
import { Globe, Save, AlertCircle } from 'lucide-react'
import { useAuthStore, useUIStore } from '@/store'

interface LanguageSettings {
  language: string
  timezone: string
  dateFormat: string
  timeFormat: string
}

const languages = [
  { code: 'en', name: 'English' },
  { code: 'id', name: 'Bahasa Indonesia' },
  { code: 'ms', name: 'Bahasa Melayu' },
  { code: 'zh', name: '中文 (Chinese)' },
  { code: 'ko', name: '한국어 (Korean)' },
]

const timezones = [
  { code: 'UTC+0', name: 'UTC (GMT)' },
  { code: 'UTC+7', name: 'Western Indonesia Time (WIB)' },
  { code: 'UTC+8', name: 'Central Indonesia Time (WITA)' },
  { code: 'UTC+9', name: 'Eastern Indonesia Time (WIT)' },
  { code: 'UTC+8', name: 'Singapore / Malaysia' },
  { code: 'UTC+12', name: 'New Zealand' },
]

const dateFormats = [
  { code: 'DD/MM/YYYY', name: 'DD/MM/YYYY (European)' },
  { code: 'MM/DD/YYYY', name: 'MM/DD/YYYY (US)' },
  { code: 'YYYY-MM-DD', name: 'YYYY-MM-DD (ISO)' },
]

const timeFormats = [
  { code: '24h', name: '24-hour (14:30)' },
  { code: '12h', name: '12-hour (2:30 PM)' },
]

export const LanguageTimezoneSettings: React.FC = () => {
  const { user } = useAuthStore()
  const { addNotification, setLanguage } = useUIStore()
  const [loading, setLoading] = useState(false)
  const [settings, setSettings] = useState<LanguageSettings>({
    language: 'en',
    timezone: 'UTC+7',
    dateFormat: 'DD/MM/YYYY',
    timeFormat: '24h',
  })

  useEffect(() => {
    // Load user preferences from localStorage
    const saved = localStorage.getItem('languageSettings')
    if (saved) {
      setSettings(JSON.parse(saved))
    }
  }, [])

  const handleChange = (key: keyof LanguageSettings, value: string) => {
    setSettings(prev => ({ ...prev, [key]: value }))
  }

  const handleSave = async () => {
    try {
      setLoading(true)
      
      // Validate settings
      if (!settings.language || !settings.timezone) {
        addNotification('error', 'Please select language and timezone')
        return
      }
      
      // Save to localStorage with timestamp
      const settingsToSave = {
        ...settings,
        savedAt: new Date().toISOString()
      }
      localStorage.setItem('languageSettings', JSON.stringify(settingsToSave))
      
      // Apply language to UI store and DOM immediately
      setLanguage(settings.language)
      document.documentElement.lang = settings.language
      
      // Store timezone in localStorage as well
      localStorage.setItem('timezone', settings.timezone)
      
      // Add small delay to show button state
      await new Promise(resolve => setTimeout(resolve, 500))
      
      addNotification('success', '✓ Language and timezone settings saved successfully!')
      console.log('[LanguageTimezone] Settings saved:', { language: settings.language, timezone: settings.timezone })
    } catch (error) {
      addNotification('error', 'Failed to save settings: ' + (error instanceof Error ? error.message : 'Unknown error'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-2xl">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Globe className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">Language & Timezone</h1>
        </div>
        <p className="text-gray-600">Customize language, timezone, and date/time formats</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
        {/* Language Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Language
          </label>
          <select
            value={settings.language}
            onChange={(e) => handleChange('language', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            {languages.map(lang => (
              <option key={lang.code} value={lang.code}>{lang.name}</option>
            ))}
          </select>
          <p className="text-xs text-gray-500 mt-1">Changes apply system-wide</p>
        </div>

        {/* Timezone Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Timezone
          </label>
          <select
            value={settings.timezone}
            onChange={(e) => handleChange('timezone', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            {timezones.map(tz => (
              <option key={tz.code} value={tz.code}>{tz.name}</option>
            ))}
          </select>
          <p className="text-xs text-gray-500 mt-1">Used for all timestamps in the system</p>
        </div>

        {/* Date Format */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Date Format
          </label>
          <div className="grid grid-cols-3 gap-2">
            {dateFormats.map(format => (
              <button
                key={format.code}
                onClick={() => handleChange('dateFormat', format.code)}
                className={`p-2 rounded border-2 text-sm transition-colors ${
                  settings.dateFormat === format.code
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                {format.code}
                <div className="text-xs text-gray-600 mt-1">{format.name}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Time Format */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Time Format
          </label>
          <div className="grid grid-cols-2 gap-2">
            {timeFormats.map(format => (
              <button
                key={format.code}
                onClick={() => handleChange('timeFormat', format.code)}
                className={`p-3 rounded border-2 text-sm transition-colors ${
                  settings.timeFormat === format.code
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                {format.name}
              </button>
            ))}
          </div>
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-blue-800">
            <p className="font-medium">Current Settings</p>
            <p className="mt-1">Language: <strong>{settings.language.toUpperCase()}</strong> | Timezone: <strong>{settings.timezone}</strong></p>
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
