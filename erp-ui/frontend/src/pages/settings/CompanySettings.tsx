/**
 * Company Settings Page (SUPERADMIN only)
 * Configure company information and policies
 */

import React, { useState, useEffect } from 'react'
import { Building2, Save } from 'lucide-react'
import { useUIStore } from '@/store'

interface CompanySettings {
  companyName: string
  companyCode: string
  industry: string
  address: string
  city: string
  province: string
  zipCode: string
  country: string
  phone: string
  email: string
  website: string
  taxNumber: string
  businessLicense: string
  logo: string
}

export const CompanySettings: React.FC = () => {
  const { addNotification } = useUIStore()
  const [loading, setLoading] = useState(false)
  const [settings, setSettings] = useState<CompanySettings>({
    companyName: '',
    companyCode: '',
    industry: '',
    address: '',
    city: '',
    province: '',
    zipCode: '',
    country: 'Indonesia',
    phone: '',
    email: '',
    website: '',
    taxNumber: '',
    businessLicense: '',
    logo: '',
  })

  useEffect(() => {
    const saved = localStorage.getItem('companySettings')
    if (saved) setSettings(JSON.parse(saved))
  }, [])

  const handleSave = async () => {
    try {
      setLoading(true)
      if (!settings.companyName || !settings.companyCode) {
        addNotification('error', 'Please fill in company name and code')
        return
      }
      const settingsToSave = {
        ...settings,
        savedAt: new Date().toISOString()
      }
      localStorage.setItem('companySettings', JSON.stringify(settingsToSave))
      await new Promise(resolve => setTimeout(resolve, 500))
      addNotification('success', 'Company settings saved successfully!')
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
          <Building2 className="w-8 h-8 text-purple-600" />
          <h1 className="text-3xl font-bold text-gray-900">Company Settings</h1>
        </div>
        <p className="text-gray-600">Manage company information and organizational details</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
        {/* Basic Info */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b">Basic Information</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Company Name *</label>
              <input 
                type="text" 
                value={settings.companyName}
                onChange={(e) => setSettings(prev => ({ ...prev, companyName: e.target.value }))}
                placeholder="Enter company name"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Company Code *</label>
              <input 
                type="text" 
                value={settings.companyCode}
                onChange={(e) => setSettings(prev => ({ ...prev, companyCode: e.target.value }))}
                placeholder="e.g., PT-2024-001"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Industry</label>
              <input 
                type="text" 
                value={settings.industry}
                onChange={(e) => setSettings(prev => ({ ...prev, industry: e.target.value }))}
                placeholder="Manufacturing, Trading, Services"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Website</label>
              <input 
                type="url" 
                value={settings.website}
                onChange={(e) => setSettings(prev => ({ ...prev, website: e.target.value }))}
                placeholder="https://example.com"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Contact Info */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b">Contact Information</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
              <input 
                type="tel" 
                value={settings.phone}
                onChange={(e) => setSettings(prev => ({ ...prev, phone: e.target.value }))}
                placeholder="+62-XXX-XXXXXX"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input 
                type="email" 
                value={settings.email}
                onChange={(e) => setSettings(prev => ({ ...prev, email: e.target.value }))}
                placeholder="contact@company.com"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Address */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b">Address</h2>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Street Address</label>
            <input 
              type="text" 
              value={settings.address}
              onChange={(e) => setSettings(prev => ({ ...prev, address: e.target.value }))}
              placeholder="Street address"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <input 
              type="text" 
              value={settings.city}
              onChange={(e) => setSettings(prev => ({ ...prev, city: e.target.value }))}
              placeholder="City"
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input 
              type="text" 
              value={settings.province}
              onChange={(e) => setSettings(prev => ({ ...prev, province: e.target.value }))}
              placeholder="Province"
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input 
              type="text" 
              value={settings.zipCode}
              onChange={(e) => setSettings(prev => ({ ...prev, zipCode: e.target.value }))}
              placeholder="Zip Code"
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input 
              type="text" 
              value={settings.country}
              onChange={(e) => setSettings(prev => ({ ...prev, country: e.target.value }))}
              placeholder="Country"
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Legal Info */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b">Legal Information</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Tax Number (NPWP)</label>
              <input 
                type="text" 
                value={settings.taxNumber}
                onChange={(e) => setSettings(prev => ({ ...prev, taxNumber: e.target.value }))}
                placeholder="XX.XXX.XXX.X-XXX.XXX"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Business License (SIUP)</label>
              <input 
                type="text" 
                value={settings.businessLicense}
                onChange={(e) => setSettings(prev => ({ ...prev, businessLicense: e.target.value }))}
                placeholder="License number"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        <button 
          onClick={handleSave} 
          disabled={loading} 
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition"
        >
          <Save size={18} /> {loading ? 'Saving...' : 'Save Company Settings'}
        </button>
      </div>
    </div>
  )
}
