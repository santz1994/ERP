/**
 * Display Preferences Settings Page
 * Configure UI theme, layout, and visual preferences
 */

import React, { useState, useEffect } from 'react'
import { Palette, Save } from 'lucide-react'
import { useUIStore } from '@/store'

interface DisplaySettings {
  theme: 'light' | 'dark' | 'auto'
  compactMode: boolean
  sidebarPosition: 'left' | 'right'
  fontSize: 'small' | 'normal' | 'large'
  colorScheme: 'blue' | 'green' | 'purple' | 'orange'
}

export const DisplayPreferencesSettings: React.FC = () => {
  const { addNotification } = useUIStore()
  const [loading, setLoading] = useState(false)
  const [settings, setSettings] = useState<DisplaySettings>({
    theme: 'light',
    compactMode: false,
    sidebarPosition: 'left',
    fontSize: 'normal',
    colorScheme: 'blue',
  })

  useEffect(() => {
    const saved = localStorage.getItem('displaySettings')
    if (saved) setSettings(JSON.parse(saved))
  }, [])

  const handleSave = async () => {
    try {
      setLoading(true)
      localStorage.setItem('displaySettings', JSON.stringify(settings))
      addNotification('success', 'Display preferences saved!')
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
          <Palette className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">Display Preferences</h1>
        </div>
        <p className="text-gray-600">Customize the appearance and layout of the system</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
        {/* Theme Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">Theme</label>
          <div className="grid grid-cols-3 gap-2">
            {['light', 'dark', 'auto'].map(t => (
              <button 
                key={t} 
                onClick={() => setSettings(prev => ({ ...prev, theme: t as any }))} 
                className={`p-3 rounded border-2 capitalize font-medium transition ${settings.theme === t ? 'border-blue-500 bg-blue-50 text-blue-900' : 'border-gray-300 hover:border-gray-400'}`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* Compact Mode */}
        <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
          <input 
            type="checkbox" 
            checked={settings.compactMode} 
            onChange={() => setSettings(prev => ({ ...prev, compactMode: !prev.compactMode }))} 
            className="w-4 h-4"
          />
          <div>
            <p className="font-medium">Compact Mode</p>
            <p className="text-xs text-gray-600">Reduces spacing for more content</p>
          </div>
        </label>

        {/* Font Size */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">Font Size</label>
          <div className="grid grid-cols-3 gap-2">
            {['small', 'normal', 'large'].map(s => (
              <button 
                key={s} 
                onClick={() => setSettings(prev => ({ ...prev, fontSize: s as any }))} 
                className={`p-3 rounded border-2 capitalize font-medium transition ${settings.fontSize === s ? 'border-blue-500 bg-blue-50 text-blue-900' : 'border-gray-300 hover:border-gray-400'}`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        {/* Color Scheme */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">Color Scheme</label>
          <div className="grid grid-cols-4 gap-2">
            {['blue', 'green', 'purple', 'orange'].map(c => (
              <button 
                key={c} 
                onClick={() => setSettings(prev => ({ ...prev, colorScheme: c as any }))} 
                className={`p-3 rounded border-2 capitalize font-medium transition ${settings.colorScheme === c ? 'border-gray-800 bg-gray-100' : 'border-gray-300 hover:border-gray-400'}`}
              >
                <div className={`w-4 h-4 rounded-full mx-auto mb-1 bg-${c}-500`}></div>
                {c}
              </button>
            ))}
          </div>
        </div>

        <button 
          onClick={handleSave} 
          disabled={loading} 
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition"
        >
          <Save size={18} /> {loading ? 'Saving...' : 'Save Preferences'}
        </button>
      </div>
    </div>
  )
}
