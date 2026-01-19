import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Link, useLocation } from 'react-router-dom';
import { BarChart3, Scissors, Zap, Sparkles, Package, Beaker, Warehouse, Users, } from 'lucide-react';
import { useAuthStore, useUIStore } from '@/store';
import { UserRole } from '@/types';
const menuItems = [
    { icon: _jsx(BarChart3, {}), label: 'Dashboard', path: '/dashboard', roles: Object.values(UserRole) },
    { icon: _jsx(BarChart3, {}), label: 'PPIC', path: '/ppic', roles: [UserRole.PPIC, UserRole.ADMIN] },
    { icon: _jsx(Scissors, {}), label: 'Cutting', path: '/cutting', roles: [UserRole.OPERATOR_CUTTING, UserRole.SPV_CUTTING, UserRole.ADMIN] },
    { icon: _jsx(Zap, {}), label: 'Sewing', path: '/sewing', roles: [UserRole.OPERATOR_SEWING, UserRole.SPV_SEWING, UserRole.ADMIN] },
    { icon: _jsx(Sparkles, {}), label: 'Finishing', path: '/finishing', roles: [UserRole.OPERATOR_FINISHING, UserRole.SPV_FINISHING, UserRole.ADMIN] },
    { icon: _jsx(Package, {}), label: 'Packing', path: '/packing', roles: [UserRole.OPERATOR_PACKING, UserRole.ADMIN] },
    { icon: _jsx(Beaker, {}), label: 'Quality', path: '/quality', roles: [UserRole.QC_INSPECTOR, UserRole.ADMIN] },
    { icon: _jsx(Warehouse, {}), label: 'Warehouse', path: '/warehouse', roles: [UserRole.WAREHOUSE_ADMIN, UserRole.ADMIN] },
    { icon: _jsx(Users, {}), label: 'Admin', path: '/admin', roles: [UserRole.ADMIN] },
];
export const Sidebar = () => {
    const { user } = useAuthStore();
    const { sidebarOpen } = useUIStore();
    const location = useLocation();
    const visibleItems = menuItems.filter((item) => user && item.roles.includes(user.role));
    return (_jsxs("div", { className: `bg-gray-900 text-white h-screen shadow-lg transition-all duration-300 ${sidebarOpen ? 'w-64' : 'w-20'}`, children: [_jsxs("div", { className: "p-4", children: [sidebarOpen && (_jsxs("div", { className: "text-center mb-8", children: [_jsx("h2", { className: "text-xl font-bold text-brand-400", children: "QK ERP" }), _jsx("p", { className: "text-xs text-gray-400", children: "Manufacturing System" })] })), _jsx("nav", { className: "space-y-2", children: visibleItems.map((item) => (_jsxs(Link, { to: item.path, className: `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${location.pathname === item.path
                                ? 'bg-brand-600 text-white'
                                : 'text-gray-300 hover:bg-gray-800'}`, title: !sidebarOpen ? item.label : undefined, children: [_jsx("div", { className: "w-6 h-6 flex-shrink-0", children: item.icon }), sidebarOpen && _jsx("span", { className: "text-sm", children: item.label })] }, item.path))) })] }), sidebarOpen && (_jsxs("div", { className: "absolute bottom-4 left-4 right-4 p-4 bg-gray-800 rounded-lg", children: [_jsx("p", { className: "text-xs text-gray-400 mb-2", children: "Version" }), _jsx("p", { className: "text-sm font-semibold", children: "1.0.0" })] }))] }));
};
