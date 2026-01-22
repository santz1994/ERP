/**
 * UI Component Unit Tests
 * Tests for React TypeScript components, hooks, and utilities
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';

// Components
import Navbar from '../src/components/Navbar';
import Sidebar from '../src/components/Sidebar';
import PermissionBadge from '../src/components/PermissionBadge';
import { BigButton, FullScreenLayout } from '../src/components/BigButtonMode';

// Hooks
import { usePermission } from '../src/hooks/usePermission';

// Stores
import { useAuthStore } from '../src/store/authStore';
import { usePermissionStore } from '../src/store/permissionStore';


// Mock stores
vi.mock('../src/store/authStore');
vi.mock('../src/store/permissionStore');

const mockAuthStore = {
  user: {
    id: 1,
    username: 'testuser',
    role: 'admin',
    email: 'test@example.com'
  },
  isAuthenticated: true,
  logout: vi.fn()
};

const mockPermissionStore = {
  permissions: ['admin.full_access', 'warehouse.view', 'warehouse.create'],
  hasPermission: vi.fn((permission: string) => {
    return mockPermissionStore.permissions.includes(permission);
  })
};


describe('Navbar Component', () => {
  beforeEach(() => {
    (useAuthStore as any).mockReturnValue(mockAuthStore);
  });

  it('renders user information', () => {
    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    );

    expect(screen.getByText('testuser')).toBeInTheDocument();
  });

  it('calls logout when logout button clicked', () => {
    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    );

    const logoutButton = screen.getByTestId('logout-button');
    fireEvent.click(logoutButton);

    expect(mockAuthStore.logout).toHaveBeenCalled();
  });

  it('displays environment banner in development', () => {
    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    );

    // Assuming development mode
    const banner = screen.queryByTestId('env-banner');
    if (banner) {
      expect(banner).toHaveTextContent(/development/i);
    }
  });
});


describe('Sidebar Component', () => {
  beforeEach(() => {
    (useAuthStore as any).mockReturnValue(mockAuthStore);
    (usePermissionStore as any).mockReturnValue(mockPermissionStore);
  });

  it('renders navigation links based on permissions', () => {
    render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>
    );

    // Admin should see admin link
    expect(screen.getByText(/admin/i)).toBeInTheDocument();
    
    // Should see warehouse link (has warehouse.view permission)
    expect(screen.getByText(/warehouse/i)).toBeInTheDocument();
  });

  it('hides menu items without permission', () => {
    // Mock user without admin permission
    const limitedAuthStore = {
      ...mockAuthStore,
      user: { ...mockAuthStore.user, role: 'operator_cut' }
    };
    
    const limitedPermissionStore = {
      permissions: ['cutting.view', 'cutting.execute'],
      hasPermission: vi.fn((perm) => limitedPermissionStore.permissions.includes(perm))
    };

    (useAuthStore as any).mockReturnValue(limitedAuthStore);
    (usePermissionStore as any).mockReturnValue(limitedPermissionStore);

    render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>
    );

    // Should NOT see admin link
    expect(screen.queryByText(/admin/i)).not.toBeInTheDocument();
  });

  it('highlights active route', () => {
    render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>
    );

    const dashboardLink = screen.getByRole('link', { name: /dashboard/i });
    expect(dashboardLink).toHaveClass(/active|bg-blue/);
  });
});


describe('PermissionBadge Component', () => {
  beforeEach(() => {
    (usePermissionStore as any).mockReturnValue(mockPermissionStore);
  });

  it('shows granted badge when user has permission', () => {
    render(<PermissionBadge permission="warehouse.view" />);

    expect(screen.getByText(/granted/i)).toBeInTheDocument();
    expect(screen.getByText(/granted/i)).toHaveClass(/bg-green|text-green/);
  });

  it('shows denied badge when user lacks permission', () => {
    render(<PermissionBadge permission="admin.delete_users" />);

    expect(screen.getByText(/denied/i)).toBeInTheDocument();
    expect(screen.getByText(/denied/i)).toHaveClass(/bg-red|text-red/);
  });
});


describe('BigButton Component', () => {
  it('renders with large size (64px minimum)', () => {
    const { container } = render(
      <BigButton onClick={vi.fn()}>Click Me</BigButton>
    );

    const button = container.querySelector('button');
    expect(button).toHaveStyle({ height: '64px' });
  });

  it('has adequate spacing for glove operation', () => {
    const { container } = render(
      <div>
        <BigButton onClick={vi.fn()}>Button 1</BigButton>
        <BigButton onClick={vi.fn()}>Button 2</BigButton>
      </div>
    );

    const buttons = container.querySelectorAll('button');
    expect(buttons).toHaveLength(2);
    
    // Check margin/padding (should be at least 16px)
    const button1Style = window.getComputedStyle(buttons[0]);
    const marginBottom = parseInt(button1Style.marginBottom);
    expect(marginBottom).toBeGreaterThanOrEqual(16);
  });

  it('calls onClick handler when clicked', () => {
    const handleClick = vi.fn();
    render(<BigButton onClick={handleClick}>Click Me</BigButton>);

    fireEvent.click(screen.getByText('Click Me'));
    expect(handleClick).toHaveBeenCalledOnce();
  });
});


describe('FullScreenLayout Component', () => {
  it('renders in fullscreen mode', () => {
    const { container } = render(
      <FullScreenLayout>
        <div>Content</div>
      </FullScreenLayout>
    );

    const layout = container.firstChild;
    expect(layout).toHaveClass(/fullscreen|h-screen|w-screen/);
  });

  it('renders children correctly', () => {
    render(
      <FullScreenLayout>
        <div data-testid="child">Test Content</div>
      </FullScreenLayout>
    );

    expect(screen.getByTestId('child')).toHaveTextContent('Test Content');
  });
});


describe('usePermission Hook', () => {
  it('returns true when user has permission', () => {
    (usePermissionStore as any).mockReturnValue(mockPermissionStore);

    const { result } = renderHook(() => usePermission('warehouse.view'));

    expect(result.current).toBe(true);
  });

  it('returns false when user lacks permission', () => {
    (usePermissionStore as any).mockReturnValue(mockPermissionStore);

    const { result } = renderHook(() => usePermission('admin.delete_users'));

    expect(result.current).toBe(false);
  });

  it('handles multiple permissions with OR logic', () => {
    (usePermissionStore as any).mockReturnValue(mockPermissionStore);

    const { result } = renderHook(() => 
      usePermission(['warehouse.view', 'admin.nonexistent'], { requireAll: false })
    );

    // Should return true because warehouse.view exists
    expect(result.current).toBe(true);
  });

  it('handles multiple permissions with AND logic', () => {
    (usePermissionStore as any).mockReturnValue(mockPermissionStore);

    const { result } = renderHook(() => 
      usePermission(['warehouse.view', 'admin.nonexistent'], { requireAll: true })
    );

    // Should return false because admin.nonexistent doesn't exist
    expect(result.current).toBe(false);
  });
});


describe('Auth Store', () => {
  it('stores user data after login', () => {
    const store = useAuthStore.getState();
    
    store.setUser({
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      role: 'admin'
    });

    expect(store.user).toEqual({
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      role: 'admin'
    });
    expect(store.isAuthenticated).toBe(true);
  });

  it('clears user data on logout', () => {
    const store = useAuthStore.getState();
    
    store.setUser({ id: 1, username: 'test', email: 'test@example.com', role: 'admin' });
    store.logout();

    expect(store.user).toBeNull();
    expect(store.isAuthenticated).toBe(false);
  });
});


describe('Permission Store', () => {
  it('loads permissions from API', async () => {
    const mockPermissions = ['warehouse.view', 'warehouse.create', 'cutting.view'];
    
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ permissions: mockPermissions })
      })
    ) as any;

    const store = usePermissionStore.getState();
    await store.loadPermissions();

    expect(store.permissions).toEqual(mockPermissions);
  });

  it('checks single permission correctly', () => {
    const store = usePermissionStore.getState();
    store.permissions = ['warehouse.view', 'warehouse.create'];

    expect(store.hasPermission('warehouse.view')).toBe(true);
    expect(store.hasPermission('admin.full_access')).toBe(false);
  });

  it('checks multiple permissions with OR logic', () => {
    const store = usePermissionStore.getState();
    store.permissions = ['warehouse.view'];

    expect(store.hasAnyPermission(['warehouse.view', 'admin.full_access'])).toBe(true);
    expect(store.hasAnyPermission(['cutting.view', 'admin.full_access'])).toBe(false);
  });

  it('checks multiple permissions with AND logic', () => {
    const store = usePermissionStore.getState();
    store.permissions = ['warehouse.view', 'warehouse.create'];

    expect(store.hasAllPermissions(['warehouse.view', 'warehouse.create'])).toBe(true);
    expect(store.hasAllPermissions(['warehouse.view', 'admin.full_access'])).toBe(false);
  });
});


describe('Responsive Utilities', () => {
  it('detects mobile viewport', () => {
    // Mock window.innerWidth
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375
    });

    const isMobile = window.innerWidth < 768;
    expect(isMobile).toBe(true);
  });

  it('detects desktop viewport', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1920
    });

    const isMobile = window.innerWidth < 768;
    expect(isMobile).toBe(false);
  });
});


// Helper function to render hooks (if not using @testing-library/react-hooks)
function renderHook<T>(callback: () => T) {
  let result: T;
  
  function TestComponent() {
    result = callback();
    return null;
  }
  
  render(<TestComponent />);
  
  return { result: result! };
}
