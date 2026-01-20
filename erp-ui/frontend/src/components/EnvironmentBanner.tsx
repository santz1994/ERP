import { useState, useEffect } from 'react';
import { api } from '@/api/client';
import { useAuthStore } from '@/store/authStore';

interface EnvironmentInfo {
  environment: string;
  developer_restrictions_active: boolean;
  developer_allowed_permissions: string[];
  developer_blocked_permissions: string[];
  current_user: {
    id: number;
    username: string;
    role: string;
    is_developer: boolean;
    is_restricted: boolean;
    can_write: boolean;
  };
  security_settings: {
    debug_mode: boolean;
    environment: string;
    jwt_expiration_hours: number;
  };
}

export function EnvironmentBanner() {
  const { user } = useAuthStore();
  const [envInfo, setEnvInfo] = useState<EnvironmentInfo | null>(null);
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    if (user?.role === 'DEVELOPER' || user?.role === 'ADMIN' || user?.role === 'SUPERADMIN') {
      fetchEnvironmentInfo();
    }
  }, [user]);

  const fetchEnvironmentInfo = async () => {
    try {
      const response = await api.get('/api/admin/environment-info');
      setEnvInfo(response.data);
    } catch (error) {
      console.error('Failed to fetch environment info:', error);
    }
  };

  if (!visible || !envInfo) return null;

  // Only show for DEVELOPER role in PRODUCTION
  if (!envInfo.current_user.is_restricted) return null;

  return (
    <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <p className="text-sm font-medium text-yellow-800">
            <strong>READ-ONLY MODE:</strong> You are logged in as DEVELOPER in PRODUCTION environment
          </p>
          <div className="mt-2 text-sm text-yellow-700">
            <p className="mb-2">Your access is restricted to VIEW operations only. Write operations are blocked:</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              {envInfo.developer_blocked_permissions.map((perm) => (
                <li key={perm}>
                  <span className="line-through">{perm.toUpperCase()}</span> - Not allowed
                </li>
              ))}
            </ul>
            <p className="mt-3 text-xs">
              <strong>Allowed:</strong> {envInfo.developer_allowed_permissions.join(', ').toUpperCase()}
            </p>
            <p className="mt-2 text-xs">
              To perform write operations, switch to DEVELOPMENT or TESTING environment.
            </p>
          </div>
        </div>
        <button
          onClick={() => setVisible(false)}
          className="flex-shrink-0 ml-3 text-yellow-500 hover:text-yellow-700"
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
}

export function EnvironmentIndicator() {
  const { user } = useAuthStore();
  const [envInfo, setEnvInfo] = useState<EnvironmentInfo | null>(null);

  useEffect(() => {
    if (user?.role === 'DEVELOPER' || user?.role === 'ADMIN' || user?.role === 'SUPERADMIN') {
      fetchEnvironmentInfo();
    }
  }, [user]);

  const fetchEnvironmentInfo = async () => {
    try {
      const response = await api.get('/api/admin/environment-info');
      setEnvInfo(response.data);
    } catch (error) {
      console.error('Failed to fetch environment info:', error);
    }
  };

  if (!envInfo) return null;

  const envColors: Record<string, string> = {
    development: 'bg-green-100 text-green-800 border-green-300',
    testing: 'bg-blue-100 text-blue-800 border-blue-300',
    production: 'bg-red-100 text-red-800 border-red-300'
  };

  const colorClass = envColors[envInfo.environment] || 'bg-gray-100 text-gray-800 border-gray-300';

  return (
    <div className={`inline-flex items-center px-2 py-1 rounded border text-xs font-medium ${colorClass}`}>
      <span className="inline-block w-2 h-2 rounded-full bg-current mr-1.5"></span>
      {envInfo.environment.toUpperCase()}
      {envInfo.current_user.is_restricted && (
        <span className="ml-2 text-[10px] bg-yellow-200 text-yellow-900 px-1 rounded">READ-ONLY</span>
      )}
    </div>
  );
}
