import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Menu, X, LogOut, Bell } from 'lucide-react';
import { useAuthStore, useUIStore } from '@/store';
import { useNavigate } from 'react-router-dom';
export const Navbar = () => {
    const { user, logout } = useAuthStore();
    const { sidebarOpen, toggleSidebar } = useUIStore();
    const navigate = useNavigate();
    const handleLogout = () => {
        logout();
        navigate('/login');
    };
    return (_jsx("nav", { className: "bg-white shadow-md border-b border-gray-200", children: _jsx("div", { className: "px-4 sm:px-6 lg:px-8 py-3", children: _jsxs("div", { className: "flex justify-between items-center", children: [_jsxs("div", { className: "flex items-center", children: [_jsx("button", { onClick: toggleSidebar, className: "p-2 rounded-md text-gray-600 hover:bg-gray-100", children: sidebarOpen ? _jsx(X, { size: 24 }) : _jsx(Menu, { size: 24 }) }), _jsx("h1", { className: "ml-4 text-2xl font-bold text-brand-600", children: "Quty Karunia ERP" })] }), _jsxs("div", { className: "flex items-center gap-4", children: [_jsxs("button", { className: "p-2 text-gray-600 hover:bg-gray-100 rounded-md relative", children: [_jsx(Bell, { size: 20 }), _jsx("span", { className: "absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full" })] }), _jsxs("div", { className: "text-right", children: [_jsx("p", { className: "text-sm font-medium text-gray-900", children: user?.full_name }), _jsx("p", { className: "text-xs text-gray-500", children: user?.role })] }), _jsx("button", { onClick: handleLogout, className: "p-2 text-gray-600 hover:bg-gray-100 rounded-md", title: "Logout", children: _jsx(LogOut, { size: 20 }) })] })] }) }) }));
};
