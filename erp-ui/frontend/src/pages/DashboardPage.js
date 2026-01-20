import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from 'react';
import { BarChart3, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';
import { useUIStore } from '@/store';
export const DashboardPage = () => {
    const { addNotification } = useUIStore();
    const [stats, setStats] = useState({
        totalMOs: 0,
        completedToday: 0,
        pendingQC: 0,
        criticalAlerts: 0,
    });
    useEffect(() => {
        // Load dashboard data
        loadDashboardStats();
    }, []);
    const loadDashboardStats = async () => {
        try {
            // This would call actual API endpoints to fetch stats
            // For now, showing placeholder data
            setStats({
                totalMOs: 42,
                completedToday: 8,
                pendingQC: 3,
                criticalAlerts: 1,
            });
        }
        catch (error) {
            addNotification('error', 'Failed to load dashboard data');
        }
    };
    return (_jsxs("div", { className: "p-6", children: [_jsxs("div", { className: "mb-8", children: [_jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Dashboard" }), _jsx("p", { className: "text-gray-600", children: "Welcome back! Here's your production overview." })] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8", children: [_jsx(StatCard, { title: "Total MOs", value: stats.totalMOs, icon: _jsx(BarChart3, { className: "w-8 h-8" }), color: "bg-blue-50 text-blue-600" }), _jsx(StatCard, { title: "Completed Today", value: stats.completedToday, icon: _jsx(CheckCircle, { className: "w-8 h-8" }), color: "bg-green-50 text-green-600" }), _jsx(StatCard, { title: "Pending QC", value: stats.pendingQC, icon: _jsx(AlertCircle, { className: "w-8 h-8" }), color: "bg-yellow-50 text-yellow-600" }), _jsx(StatCard, { title: "Critical Alerts", value: stats.criticalAlerts, icon: _jsx(TrendingUp, { className: "w-8 h-8" }), color: "bg-red-50 text-red-600" })] }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-3 gap-6", children: [_jsxs("div", { className: "lg:col-span-2 bg-white rounded-lg shadow p-6", children: [_jsx("h2", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Production Status" }), _jsxs("div", { className: "space-y-4", children: [_jsx(ProductionStatus, { dept: "Cutting", progress: 75, status: "Running" }), _jsx(ProductionStatus, { dept: "Sewing", progress: 60, status: "Running" }), _jsx(ProductionStatus, { dept: "Finishing", progress: 45, status: "Pending" }), _jsx(ProductionStatus, { dept: "Packing", progress: 30, status: "Pending" })] })] }), _jsxs("div", { className: "bg-white rounded-lg shadow p-6", children: [_jsx("h2", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Recent Alerts" }), _jsxs("div", { className: "space-y-3", children: [_jsx(AlertItem, { type: "critical", message: "Metal detector fail - Batch 001" }), _jsx(AlertItem, { type: "warning", message: "Line clearance required - Cutting" }), _jsx(AlertItem, { type: "info", message: "New MO created - MO-2024-042" })] })] })] })] }));
};
const StatCard = ({ title, value, icon, color }) => (_jsxs("div", { className: "bg-white rounded-lg shadow p-6", children: [_jsx("div", { className: `w-12 h-12 rounded-lg ${color} flex items-center justify-center mb-4`, children: icon }), _jsx("p", { className: "text-gray-600 text-sm font-medium", children: title }), _jsx("p", { className: "text-3xl font-bold text-gray-900 mt-1", children: value })] }));
const ProductionStatus = ({ dept, progress, status }) => (_jsxs("div", { children: [_jsxs("div", { className: "flex justify-between mb-2", children: [_jsx("p", { className: "text-sm font-medium text-gray-700", children: dept }), _jsx("p", { className: `text-xs font-semibold ${status === 'Running' ? 'text-green-600' :
                        status === 'Pending' ? 'text-yellow-600' :
                            'text-gray-600'}`, children: status })] }), _jsx("div", { className: "w-full bg-gray-200 rounded-full h-2", children: _jsx("div", { className: `h-2 rounded-full transition-all ${status === 'Running' ? 'bg-green-500' :
                    status === 'Pending' ? 'bg-yellow-500' :
                        'bg-gray-500'}`, style: { width: `${progress}%` } }) }), _jsxs("p", { className: "text-xs text-gray-500 mt-1", children: [progress, "% complete"] })] }));
const AlertItem = ({ type, message }) => (_jsx("div", { className: `p-3 rounded-lg border-l-4 ${type === 'critical' ? 'bg-red-50 border-red-500' :
        type === 'warning' ? 'bg-yellow-50 border-yellow-500' :
            'bg-blue-50 border-blue-500'}`, children: _jsx("p", { className: `text-sm ${type === 'critical' ? 'text-red-700' :
            type === 'warning' ? 'text-yellow-700' :
                'text-blue-700'}`, children: message }) }));
