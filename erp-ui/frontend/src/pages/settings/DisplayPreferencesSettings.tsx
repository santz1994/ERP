/**
 * Display Preferences Settings Page
 * Configure UI theme, layout, and visual preferences
 */

import React, { useState, useEffect } from 'react'
import { Palette, Save } from 'lucide-react'
import { useUIStore } from '@/store'

export const DisplayPreferencesSettings: React.FC = () => {
  const { 
    theme, 
    language, 
    compactMode, 
    sidebarPosition, 
    fontSize, 
    colorScheme,
    setTheme,
    setLanguage,
    setCompactMode,
    setSidebarPosition,
    setFontSize,
    setColorScheme,
    updateSettings,
    loadSettings
  } = useUIStore()
  
  const [loading, setLoading] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    // Load settings on component mount
    loadSettings()
  }, [loadSettings])

  const handleSave = async () => {
    try {
      setLoading(true)
      // Apply each setting to DOM immediately
      setTheme(theme)
      setLanguage(language)
      setCompactMode(compactMode)
      setSidebarPosition(sidebarPosition)
      setFontSize(fontSize)
      setColorScheme(colorScheme)
      
      // Also batch update for consistency
      updateSettings({
        theme,
        language,
        compactMode,
        sidebarPosition,
        fontSize,
        colorScheme
      })
      
      // Show success indicator
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
      console.log('[DisplayPreferences] Settings saved:', { theme, language, fontSize })
    } catch (error) {
      console.error('Failed to save settings:', error)
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
                onClick={() => setTheme(t as any)} 
                className={`p-3 rounded border-2 capitalize font-medium transition ${theme === t ? 'border-blue-500 bg-blue-50 text-blue-900' : 'border-gray-300 hover:border-gray-400'}`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* Language Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">Language</label>
          <select 
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500"
          >
            <option value="en">English</option>
            <option value="id">Bahasa Indonesia</option>
            <option value="es">Español</option>
            <option value="fr">Français</option>
            <option value="de">Deutsch</option>
            <option value="zh">中文</option>
          </select>
        </div>

        {/* Compact Mode */}
        <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
          <input 
            type="checkbox" 
            checked={compactMode} 
            onChange={() => setCompactMode(!compactMode)} 
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
                onClick={() => setFontSize(s as any)} 
                className={`p-3 rounded border-2 capitalize font-medium transition ${fontSize === s ? 'border-blue-500 bg-blue-50 text-blue-900' : 'border-gray-300 hover:border-gray-400'}`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        {/* Sidebar Position */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">Sidebar Position</label>
          <div className="grid grid-cols-2 gap-2">
            {['left', 'right'].map(pos => (
              <button 
                key={pos} 
                onClick={() => setSidebarPosition(pos as any)} 
                className={`p-3 rounded border-2 capitalize font-medium transition ${sidebarPosition === pos ? 'border-blue-500 bg-blue-50 text-blue-900' : 'border-gray-300 hover:border-gray-400'}`}
              >
                {pos}
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
                onClick={() => setColorScheme(c as any)} 
                className={`p-3 rounded border-2 capitalize font-medium transition ${colorScheme === c ? 'border-gray-800 bg-gray-100' : 'border-gray-300 hover:border-gray-400'}`}
              >
                <div className={`w-4 h-4 rounded-full mx-auto mb-1 bg-${c}-500`}></div>
                {c}
              </button>
            ))}
          </div>
        </div>

        {saved && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-green-800 font-medium">Settings saved and applied successfully!</p>
          </div>
        )}

        <button 
          onClick={handleSave} 
          disabled={loading} 
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition"
        >
          <Save size={18} /> {loading ? 'Saving...' : 'Save & Apply Preferences'}
        </button>
      </div>
    </div>
  )
}
