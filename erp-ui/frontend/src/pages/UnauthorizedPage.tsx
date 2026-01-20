/**
 * 403 Unauthorized Page
 * 
 * Displayed when user tries to access a resource without sufficient permissions
 * ISO 27001 compliant - clear messaging without exposing system structure
 */

import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store'

export const UnauthorizedPage: React.FC = () => {
  const navigate = useNavigate()
  const { user } = useAuthStore()

  const handleGoBack = () => {
    navigate(-1)
  }

  const handleGoHome = () => {
    navigate('/dashboard')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white shadow-xl rounded-lg p-8">
        {/* Error Icon */}
        <div className="flex justify-center mb-6">
          <div className="rounded-full bg-red-100 p-3">
            <svg
              className="h-12 w-12 text-red-600"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
        </div>

        {/* Title */}
        <h1 className="text-3xl font-bold text-center text-gray-900 mb-2">
          403 - Access Denied
        </h1>

        {/* Message */}
        <p className="text-center text-gray-600 mb-6">
          You don't have permission to access this resource.
        </p>

        {/* User Info */}
        {user && (
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <div className="text-sm text-gray-700">
              <p>
                <span className="font-semibold">Current User:</span>{' '}
                {user.full_name}
              </p>
              <p>
                <span className="font-semibold">Role:</span> {user.role}
              </p>
              {user.department && (
                <p>
                  <span className="font-semibold">Department:</span>{' '}
                  {user.department}
                </p>
              )}
            </div>
          </div>
        )}

        {/* Help Text */}
        <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-blue-400"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-blue-700">
                If you believe you should have access to this resource, please
                contact your system administrator or IT support.
              </p>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col space-y-3">
          <button
            onClick={handleGoHome}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Go to Dashboard
          </button>
          <button
            onClick={handleGoBack}
            className="w-full bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium py-2 px-4 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
          >
            Go Back
          </button>
        </div>

        {/* Security Notice */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            All access attempts are logged for security purposes
            <br />
            ISO 27001 Compliant | A.12.4.1 Event Logging
          </p>
        </div>
      </div>
    </div>
  )
}

export default UnauthorizedPage
