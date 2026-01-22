// Playwright E2E Test Suite - ERP Frontend
// Test UI/UX, Navigation, Authentication, and Production Workflows

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:5173';
const API_URL = 'http://localhost:8000/api/v1';

const TEST_USER = {
  username: 'developer',
  password: 'password123'
};

test.describe('ERP Frontend E2E Tests', () => {
  
  // ==========================================================================
  // AUTHENTICATION TESTS
  // ==========================================================================
  
  test.describe('Authentication', () => {
    
    test('should load login page', async ({ page }) => {
      await page.goto(BASE_URL);
      await expect(page).toHaveURL(/.*login/);
      await expect(page.locator('h1, h2')).toContainText(/login|sign in/i);
    });
    
    test('should login successfully with valid credentials', async ({ page }) => {
      await page.goto(BASE_URL);
      
      // Fill login form
      await page.fill('input[name="username"], input[type="text"]', TEST_USER.username);
      await page.fill('input[name="password"], input[type="password"]', TEST_USER.password);
      
      // Submit
      await page.click('button[type="submit"]');
      
      // Wait for navigation to dashboard
      await page.waitForURL(/.*dashboard|home/i, { timeout: 10000 });
      
      // Verify we're logged in
      expect(page.url()).not.toContain('login');
    });
    
    test('should reject invalid credentials', async ({ page }) => {
      await page.goto(BASE_URL);
      
      await page.fill('input[name="username"], input[type="text"]', 'invalid_user');
      await page.fill('input[name="password"], input[type="password"]', 'wrong_password');
      await page.click('button[type="submit"]');
      
      // Should show error message
      await expect(page.locator('text=/invalid|error|incorrect/i')).toBeVisible({ timeout: 5000 });
    });
    
    test('should logout successfully', async ({ page }) => {
      // Login first
      await page.goto(BASE_URL);
      await page.fill('input[name="username"], input[type="text"]', TEST_USER.username);
      await page.fill('input[name="password"], input[type="password"]', TEST_USER.password);
      await page.click('button[type="submit"]');
      await page.waitForURL(/.*dashboard|home/i, { timeout: 10000 });
      
      // Logout
      await page.click('button:has-text("Logout"), button:has-text("Sign Out")');
      
      // Should redirect to login
      await page.waitForURL(/.*login/i, { timeout: 5000 });
    });
  });
  
  // ==========================================================================
  // UI-01: DYNAMIC SIDEBAR TEST
  // ==========================================================================
  
  test.describe('UI-01: Dynamic Sidebar', () => {
    
    test('should show sidebar after login', async ({ page }) => {
      // Login
      await page.goto(BASE_URL);
      await page.fill('input[name="username"], input[type="text"]', TEST_USER.username);
      await page.fill('input[name="password"], input[type="password"]', TEST_USER.password);
      await page.click('button[type="submit"]');
      await page.waitForURL(/.*dashboard|home/i, { timeout: 10000 });
      
      // Check sidebar is visible
      const sidebar = page.locator('nav, aside, [class*="sidebar"]').first();
      await expect(sidebar).toBeVisible();
    });
    
    test('should display navigation menu items', async ({ page }) => {
      // Login
      await page.goto(BASE_URL);
      await page.fill('input[name="username"], input[type="text"]', TEST_USER.username);
      await page.fill('input[name="password"], input[type="password"]', TEST_USER.password);
      await page.click('button[type="submit"]');
      await page.waitForURL(/.*dashboard|home/i, { timeout: 10000 });
      
      // Check for common menu items
      await expect(page.locator('text=/dashboard/i').first()).toBeVisible();
    });
  });
  
  // ==========================================================================
  // UI-03: RESPONSIVE TABLE TEST
  // ==========================================================================
  
  test.describe('UI-03: Responsive Table', () => {
    
    test('should load and display data tables', async ({ page }) => {
      // Login
      await page.goto(BASE_URL);
      await page.fill('input[name="username"], input[type="text"]', TEST_USER.username);
      await page.fill('input[name="password"], input[type="password"]', TEST_USER.password);
      await page.click('button[type="submit"]');
      await page.waitForURL(/.*dashboard|home/i, { timeout: 10000 });
      
      // Navigate to any page with table (e.g., PPIC, Warehouse)
      await page.click('text=/ppic|warehouse|cutting|sewing/i', { timeout: 5000 });
      
      // Wait for table to load
      await page.waitForSelector('table, [class*="table"]', { timeout: 10000 });
      
      // Verify table exists
      const table = page.locator('table, [class*="table"]').first();
      await expect(table).toBeVisible();
    });
    
    test('should handle large datasets without crashing', async ({ page }) => {
      // Login
      await page.goto(BASE_URL);
      await page.fill('input[name="username"], input[type="text"]', TEST_USER.username);
      await page.fill('input[name="password"], input[type="password"]', TEST_USER.password);
      await page.click('button[type="submit"]');
      await page.waitForURL(/.*dashboard|home/i, { timeout: 10000 });
      
      // Try to load audit trail (large dataset)
      await page.goto(`${BASE_URL}/audit-trail`, { waitUntil: 'domcontentloaded' });
      
      // Page should not crash
      await page.waitForLoadState('networkidle', { timeout: 30000 });
      expect(page.url()).toContain('audit-trail');
    });
  });
  
  // ==========================================================================
  // UI-04: SESSION TIMEOUT TEST
  // ==========================================================================
  
  test.describe('UI-04: Session Persistence', () => {
    
    test('should maintain session after page refresh', async ({ page }) => {
      // Login
      await page.goto(BASE_URL);
      await page.fill('input[name="username"], input[type="text"]', TEST_USER.username);
      await page.fill('input[name="password"], input[type="password"]', TEST_USER.password);
      await page.click('button[type="submit"]');
      await page.waitForURL(/.*dashboard|home/i, { timeout: 10000 });
      
      const urlBeforeRefresh = page.url();
      
      // Refresh page
      await page.reload();
      
      // Should still be logged in (not redirected to login)
      await page.waitForLoadState('networkidle');
      expect(page.url()).not.toContain('login');
    });
  });
  
  // ==========================================================================
  // NAVBAR TEST
  // ==========================================================================
  
  test.describe('Navbar Visibility', () => {
    
    test('should show navbar after login', async ({ page }) => {
      // Login
      await page.goto(BASE_URL);
      await page.fill('input[name="username"], input[type="text"]', TEST_USER.username);
      await page.fill('input[name="password"], input[type="password"]', TEST_USER.password);
      await page.click('button[type="submit"]');
      await page.waitForURL(/.*dashboard|home/i, { timeout: 10000 });
      
      // Check navbar is visible
      const navbar = page.locator('header, [class*="navbar"], [class*="topbar"]').first();
      await expect(navbar).toBeVisible();
    });
  });
  
  // ==========================================================================
  // PRODUCTION WORKFLOW TEST
  // ==========================================================================
  
  test.describe('Production Workflow', () => {
    
    test('should navigate to PPIC module', async ({ page }) => {
      // Login
      await page.goto(BASE_URL);
      await page.fill('input[name="username"], input[type="text"]', TEST_USER.username);
      await page.fill('input[name="password"], input[type="password"]', TEST_USER.password);
      await page.click('button[type="submit"]');
      await page.waitForURL(/.*dashboard|home/i, { timeout: 10000 });
      
      // Click PPIC menu
      await page.click('text=/ppic/i', { timeout: 5000 });
      
      // Verify we're on PPIC page
      await page.waitForURL(/.*ppic/i, { timeout: 5000 });
      expect(page.url()).toContain('ppic');
    });
    
    test('should navigate to Warehouse module', async ({ page }) => {
      // Login
      await page.goto(BASE_URL);
      await page.fill('input[name="username"], input[type="text"]', TEST_USER.username);
      await page.fill('input[name="password"], input[type="password"]', TEST_USER.password);
      await page.click('button[type="submit"]');
      await page.waitForURL(/.*dashboard|home/i, { timeout: 10000 });
      
      // Click Warehouse menu
      await page.click('text=/warehouse|gudang/i', { timeout: 5000 });
      
      // Verify navigation
      await page.waitForLoadState('networkidle');
      expect(page.url()).toMatch(/warehouse|gudang/i);
    });
  });
  
  // ==========================================================================
  // PERFORMANCE TEST
  // ==========================================================================
  
  test.describe('Performance', () => {
    
    test('should load dashboard within 3 seconds', async ({ page }) => {
      await page.goto(BASE_URL);
      await page.fill('input[name="username"], input[type="text"]', TEST_USER.username);
      await page.fill('input[name="password"], input[type="password"]', TEST_USER.password);
      
      const startTime = Date.now();
      await page.click('button[type="submit"]');
      await page.waitForURL(/.*dashboard|home/i, { timeout: 10000 });
      const loadTime = Date.now() - startTime;
      
      expect(loadTime).toBeLessThan(3000);
    });
  });
});
