import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore, useUIStore } from '@/store'
import { LogIn, Factory, ShieldCheck, ArrowRight, TrendingUp, Shield, Users } from 'lucide-react'

export const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuthStore()
  const { addNotification } = useUIStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setLoading(true)
      await login(username, password)
      addNotification('success', `Welcome back, ${username}!`)
      navigate('/dashboard')
    } catch (error: any) {
      addNotification('error', error.response?.data?.detail || 'Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex bg-white font-sans">
      
      {/* LEFT SIDE - BRANDING / VISUAL */}
      <div className="hidden lg:flex lg:w-1/2 bg-brand-900 relative overflow-hidden flex-col justify-between p-12 text-white">
        <div className="absolute inset-0 bg-gradient-to-br from-brand-800 to-slate-900 opacity-90 z-0"></div>
        {/* Pattern Overlay */}
        <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'radial-gradient(#ffffff 1px, transparent 1px)', backgroundSize: '24px 24px' }}></div>
        
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-white/10 backdrop-blur-sm rounded-lg flex items-center justify-center border border-white/20">
              <Factory size={20} />
            </div>
            <span className="text-xl font-bold tracking-tight">Quty Karunia ERP</span>
          </div>
          <h1 className="text-5xl font-extrabold leading-tight mb-4">
            Manage Production <br/>
            <span className="text-brand-300">With Precision.</span>
          </h1>
          <p className="text-brand-100 max-w-md text-lg leading-relaxed">
            Sistem terintegrasi untuk manajemen PPIC, Produksi, Gudang, dan Distribusi yang efisien dan real-time.
          </p>
          
          <div className="grid grid-cols-3 gap-6 mt-12">
            <div className="text-center">
              <div className="w-12 h-12 bg-brand-500/20 rounded-full flex items-center justify-center mx-auto mb-2">
                <TrendingUp className="w-6 h-6 text-brand-300" />
              </div>
              <p className="text-sm text-brand-200 font-medium">Real-time<br/>Monitoring</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-brand-500/20 rounded-full flex items-center justify-center mx-auto mb-2">
                <Shield className="w-6 h-6 text-brand-300" />
              </div>
              <p className="text-sm text-brand-200 font-medium">Secure<br/>Access</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-brand-500/20 rounded-full flex items-center justify-center mx-auto mb-2">
                <Users className="w-6 h-6 text-brand-300" />
              </div>
              <p className="text-sm text-brand-200 font-medium">Multi-role<br/>Support</p>
            </div>
          </div>
        </div>

        <div className="relative z-10 flex gap-8 text-sm text-brand-200">
          <div className="flex items-center gap-2">
            <ShieldCheck size={16} />
            <span>Secure Enterprise System</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span>System Operational</span>
          </div>
        </div>
      </div>

      {/* RIGHT SIDE - LOGIN FORM */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-slate-50">
        <div className="w-full max-w-md bg-white p-10 rounded-2xl shadow-xl border border-slate-100">
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900">Sign in to your account</h2>
            <p className="text-slate-500 mt-2 text-sm">Masukan kredensial Anda untuk mengakses sistem.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all outline-none text-slate-800 placeholder-slate-400"
                placeholder="ex: operator_cutting"
                autoComplete="username"
                required
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-sm font-semibold text-slate-700">Password</label>
                <a href="#" className="text-xs text-brand-600 hover:text-brand-700 font-medium">Forgot password?</a>
              </div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all outline-none text-slate-800 placeholder-slate-400"
                placeholder="••••••••"
                autoComplete="current-password"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-brand-600 hover:bg-brand-700 active:bg-brand-800 text-white font-bold py-3.5 px-4 rounded-xl transition-all shadow-lg shadow-brand-500/30 flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed mt-4 group"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <LogIn size={20} />
                  <span>Sign In</span>
                  <ArrowRight size={16} className="opacity-0 -ml-2 group-hover:opacity-100 group-hover:ml-0 transition-all" />
                </>
              )}
            </button>
          </form>
          
          {/* Demo Credentials Hint */}
          <div className="mt-8 pt-6 border-t border-slate-100">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Demo Access (Pass: password123)</p>
            <div className="grid grid-cols-2 gap-2 text-xs text-slate-600">
              <code className="bg-slate-100 px-2 py-1 rounded">admin</code>
              <code className="bg-slate-100 px-2 py-1 rounded">developer</code>
              <code className="bg-slate-100 px-2 py-1 rounded">ppic_manager</code>
              <code className="bg-slate-100 px-2 py-1 rounded">operator_cut</code>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
