import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect } from 'react';
import { X, CheckCircle, AlertCircle, XCircle, Info } from 'lucide-react';
import { useUIStore } from '@/store';
export const NotificationCenter = () => {
    const { notifications, removeNotification } = useUIStore();
    return (_jsx("div", { className: "fixed top-20 right-4 z-50 space-y-2 max-w-sm", children: notifications.map((notif) => (_jsx(Notification, { notification: notif, onClose: () => removeNotification(notif.id) }, notif.id))) }));
};
const Notification = ({ notification, onClose }) => {
    useEffect(() => {
        const timer = setTimeout(onClose, 5000);
        return () => clearTimeout(timer);
    }, [onClose]);
    const bgColor = {
        success: 'bg-green-50 border-green-200',
        error: 'bg-red-50 border-red-200',
        warning: 'bg-yellow-50 border-yellow-200',
        info: 'bg-blue-50 border-blue-200',
    }[notification.type];
    const textColor = {
        success: 'text-green-800',
        error: 'text-red-800',
        warning: 'text-yellow-800',
        info: 'text-blue-800',
    }[notification.type];
    const Icon = {
        success: CheckCircle,
        error: XCircle,
        warning: AlertCircle,
        info: Info,
    }[notification.type];
    return (_jsxs("div", { className: `flex items-center gap-3 p-4 border rounded-lg ${bgColor} animate-slide-in`, children: [_jsx(Icon, { className: `w-5 h-5 ${textColor} flex-shrink-0` }), _jsx("p", { className: `flex-1 text-sm ${textColor}`, children: notification.message }), _jsx("button", { onClick: onClose, className: `flex-shrink-0 ${textColor} hover:opacity-70`, children: _jsx(X, { size: 18 }) })] }));
};
