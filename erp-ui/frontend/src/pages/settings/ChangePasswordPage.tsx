import React, { useState } from 'react'
import { Lock, Eye, EyeOff, CheckCircle, XCircle } from 'lucide-react'

export const ChangePasswordPage: React.FC = () => {
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showCurrentPassword, setShowCurrentPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  // Password strength validation
  const hasUppercase = /[A-Z]/.test(newPassword)
  const hasLowercase = /[a-z]/.test(newPassword)
  const hasNumber = /[0-9]/.test(newPassword)
  const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(newPassword)
  const hasMinLength = newPassword.length >= 8
  const passwordsMatch = newPassword && newPassword === confirmPassword

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Implement password change API call
    console.log('Password change requested')
  }

  return (
    <div className="p-6">
      <div className="max-w-2xl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Lock className="text-brand-600" size={32} />
            Change Password
          </h1>
          <p className="text-gray-600 mt-2">Update your account password</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 space-y-6">
          {/* Current Password */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Current Password *
            </label>
            <div className="relative">
              <input
                type={showCurrentPassword ? 'text' : 'password'}
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent pr-10"
                required
              />
              <button
                type="button"
                onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500"
              >
                {showCurrentPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
            <a href="#" className="text-sm text-brand-600 hover:underline mt-1 inline-block">
              Forgot password?
            </a>
          </div>

          {/* New Password */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              New Password *
            </label>
            <div className="relative">
              <input
                type={showNewPassword ? 'text' : 'password'}
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent pr-10"
                required
              />
              <button
                type="button"
                onClick={() => setShowNewPassword(!showNewPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500"
              >
                {showNewPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
            
            {/* Password Strength Indicators */}
            {newPassword && (
              <div className="mt-3 space-y-1 text-sm">
                <div className="flex items-center gap-2">
                  {hasUppercase ? <CheckCircle size={16} className="text-green-600" /> : <XCircle size={16} className="text-gray-400" />}
                  <span className={hasUppercase ? 'text-green-600' : 'text-gray-600'}>Uppercase letter (A-Z)</span>
                </div>
                <div className="flex items-center gap-2">
                  {hasLowercase ? <CheckCircle size={16} className="text-green-600" /> : <XCircle size={16} className="text-gray-400" />}
                  <span className={hasLowercase ? 'text-green-600' : 'text-gray-600'}>Lowercase letter (a-z)</span>
                </div>
                <div className="flex items-center gap-2">
                  {hasNumber ? <CheckCircle size={16} className="text-green-600" /> : <XCircle size={16} className="text-gray-400" />}
                  <span className={hasNumber ? 'text-green-600' : 'text-gray-600'}>Number (0-9)</span>
                </div>
                <div className="flex items-center gap-2">
                  {hasSpecial ? <CheckCircle size={16} className="text-green-600" /> : <XCircle size={16} className="text-gray-400" />}
                  <span className={hasSpecial ? 'text-green-600' : 'text-gray-600'}>Special character (!@#$%)</span>
                </div>
                <div className="flex items-center gap-2">
                  {hasMinLength ? <CheckCircle size={16} className="text-green-600" /> : <XCircle size={16} className="text-gray-400" />}
                  <span className={hasMinLength ? 'text-green-600' : 'text-gray-600'}>At least 8 characters</span>
                </div>
              </div>
            )}
          </div>

          {/* Confirm Password */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Confirm Password *
            </label>
            <div className="relative">
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent pr-10"
                required
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500"
              >
                {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
            {confirmPassword && !passwordsMatch && (
              <p className="text-sm text-red-600 mt-1">Passwords do not match</p>
            )}
          </div>

          {/* Actions */}
          <div className="flex justify-between items-center pt-4 border-t">
            <p className="text-sm text-gray-500">Last changed: 45 days ago</p>
            <div className="flex gap-3">
              <button
                type="button"
                className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={!currentPassword || !newPassword || !passwordsMatch || !hasUppercase || !hasLowercase || !hasNumber || !hasMinLength}
                className="px-6 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Save Changes
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ChangePasswordPage
