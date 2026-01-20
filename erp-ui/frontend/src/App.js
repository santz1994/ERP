import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store';
import { Navbar } from '@/components/Navbar';
import { Sidebar } from '@/components/Sidebar';
import { NotificationCenter } from '@/components/NotificationCenter';
import { LoginPage } from '@/pages/LoginPage';
import { DashboardPage } from '@/pages/DashboardPage';
// Placeholder for other pages
const PlaceholderPage = ({ title }) => (_jsxs("div", { className: "p-6", children: [_jsx("h1", { className: "text-3xl font-bold text-gray-900", children: title }), _jsx("p", { className: "text-gray-600 mt-2", children: "Page under development..." })] }));
const ProtectedLayout = ({ children }) => (_jsxs("div", { className: "flex h-screen bg-gray-100", children: [_jsx(Sidebar, {}), _jsxs("div", { className: "flex-1 flex flex-col overflow-hidden", children: [_jsx(Navbar, {}), _jsx("main", { className: "flex-1 overflow-auto", children: children })] }), _jsx(NotificationCenter, {})] }));
function App() {
    const { user, loadUserFromStorage } = useAuthStore();
    useEffect(() => {
        loadUserFromStorage();
    }, []);
    if (!user) {
        return _jsx(LoginPage, {});
    }
    return (_jsx(Router, { children: _jsxs(Routes, { children: [_jsx(Route, { path: "/login", element: _jsx(LoginPage, {}) }), _jsx(Route, { path: "/dashboard", element: _jsx(ProtectedLayout, { children: _jsx(DashboardPage, {}) }) }), _jsx(Route, { path: "/ppic", element: _jsx(ProtectedLayout, { children: _jsx(PlaceholderPage, { title: "PPIC - Manufacturing Planning" }) }) }), _jsx(Route, { path: "/cutting", element: _jsx(ProtectedLayout, { children: _jsx(PlaceholderPage, { title: "Cutting Department" }) }) }), _jsx(Route, { path: "/sewing", element: _jsx(ProtectedLayout, { children: _jsx(PlaceholderPage, { title: "Sewing Department" }) }) }), _jsx(Route, { path: "/finishing", element: _jsx(ProtectedLayout, { children: _jsx(PlaceholderPage, { title: "Finishing Department" }) }) }), _jsx(Route, { path: "/packing", element: _jsx(ProtectedLayout, { children: _jsx(PlaceholderPage, { title: "Packing Department" }) }) }), _jsx(Route, { path: "/quality", element: _jsx(ProtectedLayout, { children: _jsx(PlaceholderPage, { title: "Quality Control" }) }) }), _jsx(Route, { path: "/warehouse", element: _jsx(ProtectedLayout, { children: _jsx(PlaceholderPage, { title: "Warehouse Management" }) }) }), _jsx(Route, { path: "/admin", element: _jsx(ProtectedLayout, { children: _jsx(PlaceholderPage, { title: "System Administration" }) }) }), _jsx(Route, { path: "/", element: _jsx(Navigate, { to: "/dashboard", replace: true }) })] }) }));
}
export default App;
