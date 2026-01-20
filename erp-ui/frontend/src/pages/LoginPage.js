import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore, useUIStore } from '@/store';
import { LogIn } from 'lucide-react';
export const LoginPage = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuthStore();
    const { addNotification } = useUIStore();
    const navigate = useNavigate();
    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            setLoading(true);
            await login(username, password);
            addNotification('success', 'Login successful!');
            navigate('/dashboard');
        }
        catch (error) {
            addNotification('error', error.response?.data?.detail || 'Login failed');
        }
        finally {
            setLoading(false);
        }
    };
    return (_jsx("div", { className: "min-h-screen bg-gradient-to-br from-brand-600 to-brand-700 flex items-center justify-center p-4", children: _jsxs("div", { className: "bg-white rounded-lg shadow-xl w-full max-w-md p-8", children: [_jsxs("div", { className: "text-center mb-8", children: [_jsx("h1", { className: "text-3xl font-bold text-gray-900 mb-2", children: "Quty Karunia ERP" }), _jsx("p", { className: "text-gray-600", children: "Manufacturing Execution System" })] }), _jsxs("form", { onSubmit: handleSubmit, className: "space-y-6", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Username" }), _jsx("input", { type: "text", value: username, onChange: (e) => setUsername(e.target.value), className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-600 focus:border-transparent", placeholder: "Enter your username", required: true })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Password" }), _jsx("input", { type: "password", value: password, onChange: (e) => setPassword(e.target.value), className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-600 focus:border-transparent", placeholder: "Enter your password", required: true })] }), _jsxs("button", { type: "submit", disabled: loading, className: "w-full bg-brand-600 hover:bg-brand-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50", children: [_jsx(LogIn, { size: 20 }), loading ? 'Logging in...' : 'Login'] })] }), _jsxs("div", { className: "mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200", children: [_jsx("p", { className: "text-xs text-gray-600 mb-2", children: _jsx("strong", { children: "Demo Credentials:" }) }), _jsxs("ul", { className: "text-xs text-gray-600 space-y-1", children: [_jsx("li", { children: "Admin: admin / Admin@123" }), _jsx("li", { children: "Operator: operator_cutting / Op@123" }), _jsx("li", { children: "QC: qc_inspector / QC@123" })] })] })] }) }));
};
