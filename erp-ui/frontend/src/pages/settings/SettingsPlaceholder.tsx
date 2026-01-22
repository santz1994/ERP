import React from 'react'
import { Settings } from 'lucide-react'

interface SettingsPlaceholderProps {
  title: string
  description: string
}

export const SettingsPlaceholder: React.FC<SettingsPlaceholderProps> = ({ title, description }) => {
  return (
    <div className="p-6">
      <div className="max-w-4xl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Settings className="text-brand-600" size={32} />
            {title}
          </h1>
          <p className="text-gray-600 mt-2">{description}</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <div className="inline-block p-4 bg-brand-100 rounded-full mb-4">
            <Settings className="text-brand-600" size={48} />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Coming Soon
          </h2>
          <p className="text-gray-600 mb-6">
            This settings page is currently under development.
          </p>
          <div className="text-sm text-gray-500">
            <p>Expected features:</p>
            <ul className="mt-2 space-y-1">
              <li>• {description}</li>
              <li>• User-friendly interface</li>
              <li>• Real-time updates</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
