# 🧪 Testing Guide - Session 12.1
**Auth Persistence & Navbar Enhancement Testing**
**Date**: January 20, 2026

---

## ✅ Quick Testing Checklist

### 1. Auth Persistence Test (Critical Fix)

**Before Fix**: Refresh → Redirect to login
**After Fix**: Refresh → Stay on same page

**Testing Steps**:
1. Open browser: http://localhost:3001
2. Login with credentials:
   - Username: `admin`
   - Password: `Admin@123456`
3. ✅ Should redirect to dashboard
4. Navigate to any page (e.g., PPIC, Cutting, etc.)
5. Press F5 to refresh browser
6. ✅ Should stay on the same page (NO redirect to login)
7. Check browser console (F12)
8. ✅ No errors should appear
9. Check localStorage:
   ```javascript
   localStorage.getItem('access_token')  // Should show token
   localStorage.getItem('user')          // Should show user JSON
   ```
10. ✅ Both should contain valid data

**Expected Results**:
- ✅ User stays logged in after refresh
- ✅ Current page is preserved
- ✅ No redirect to login
- ✅ Navigation continues to work

---

### 2. Login Redirect Test

**Before Fix**: Login 200 OK but no redirect
**After Fix**: Login → Auto redirect to dashboard

**Testing Steps**:
1. Logout (click user icon → Logout)
2. Should return to login page
3. Login again with:
   - Username: `admin`
   - Password: `Admin@123456`
4. ✅ Should automatically redirect to /dashboard
5. Check URL bar: `http://localhost:3001/dashboard`
6. ✅ Dashboard should load with data

**Expected Results**:
- ✅ Automatic redirect after successful login
- ✅ Dashboard loads immediately
- ✅ User info appears in navbar
- ✅ No manual navigation needed

---

### 3. Navbar Dropdown Menu Test

**New Feature**: Production menu with dropdown

**Testing Steps**:
1. Login as admin
2. Look at left sidebar
3. Find "Production" menu item with Factory icon
4. ✅ Should see chevron (►) indicating dropdown
5. Click on "Production"
6. ✅ Should expand to show 5 submenu items:
   - Cutting (Scissors icon)
   - Embroidery (Palette icon)
   - Sewing (Zap icon)
   - Finishing (Sparkles icon)
   - Packing (Package icon)
7. Click on "Cutting"
8. ✅ Should navigate to /cutting page
9. ✅ "Production" parent should be highlighted
10. ✅ "Cutting" submenu should be highlighted
11. Click "Production" again
12. ✅ Dropdown should collapse

**Expected Results**:
- ✅ Smooth expand/collapse animation
- ✅ Active state shows on parent + submenu
- ✅ Indented submenu with border
- ✅ All 5 production modules accessible
- ✅ Icons visible and correct

---

### 4. Sidebar Collapse Test

**Testing Steps**:
1. Click hamburger menu icon (≡) in navbar
2. ✅ Sidebar should collapse to narrow width
3. ✅ Icons remain visible, text hidden
4. Hover over "Production" icon
5. ✅ Tooltip should show "Production"
6. Click collapsed "Production" icon
7. ✅ Dropdown should NOT show (sidebar collapsed)
8. Click hamburger icon again to expand
9. ✅ Sidebar expands to full width
10. Click "Production"
11. ✅ Dropdown works again

**Expected Results**:
- ✅ Collapse/expand animation smooth
- ✅ Icons remain visible when collapsed
- ✅ Tooltips appear on hover
- ✅ Dropdown disabled when collapsed
- ✅ State preserved after expand

---

### 5. Role-Based Access Test

**Testing Steps**:
1. Login as admin
2. Check visible menu items:
   - ✅ Dashboard
   - ✅ Purchasing
   - ✅ PPIC
   - ✅ Production (with all 5 submenus)
   - ✅ Warehouse
   - ✅ Finish Goods
   - ✅ QC
   - ✅ Reports
   - ✅ Admin
3. All items should be visible for admin role

**Note**: To test other roles, create users with different roles and verify only appropriate menus appear.

---

### 6. Pages Content Verification

**All Pages Should Load Without Errors**:

| Page | URL | Expected Content | Status |
|------|-----|------------------|--------|
| Dashboard | /dashboard | Analytics, charts, stats | ✅ |
| PPIC | /ppic | Manufacturing orders, BOM | ✅ |
| Purchasing | /purchasing | Purchase orders | ✅ |
| Cutting | /cutting | Work orders, tracking | ✅ |
| Embroidery | /embroidery | Work orders, designs | ✅ |
| Sewing | /sewing | Work orders, lines | ✅ |
| Finishing | /finishing | Work orders, stuffing | ✅ |
| Packing | /packing | Work orders, cartons | ✅ |
| Warehouse | /warehouse | Inventory, barcode | ✅ |
| Finish Goods | /finishgoods | Shipments | ✅ |
| QC | /quality | Inspections, tests | ✅ |
| Reports | /reports | Production reports | ✅ |
| Admin | /admin | System admin | ✅ |

**Testing Steps for Each Page**:
1. Navigate to page via sidebar menu
2. ✅ Page loads without errors
3. ✅ UI components visible
4. ✅ No blank/white screen
5. Check browser console (F12)
6. ✅ No JavaScript errors
7. Press F5 to refresh
8. ✅ Page reloads successfully
9. ✅ Still logged in (no redirect)

---

## 🔍 Browser Console Checks

### Check Auth State
Open browser console (F12) and run:
```javascript
// Check localStorage
console.log('Token:', localStorage.getItem('access_token'))
console.log('User:', JSON.parse(localStorage.getItem('user')))

// Check auth store (if using React DevTools)
// Should show: { user: {...}, token: "...", initialized: true }
```

### Expected Output:
```javascript
Token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." // Long JWT token
User: {
  id: 1,
  username: "admin",
  email: "admin@example.com",
  full_name: "System Administrator",
  role: "ADMIN",
  is_active: true,
  created_at: "2026-01-20T..."
}
```

---

## 🚨 Common Issues & Solutions

### Issue 1: Still Redirecting to Login After Refresh
**Symptoms**: F5 refresh → Redirect to login
**Possible Causes**:
- Frontend not reloaded with new code
- Browser cache not cleared

**Solutions**:
1. Hard refresh: Ctrl + Shift + R (Windows) or Cmd + Shift + R (Mac)
2. Clear browser cache and localStorage:
   ```javascript
   localStorage.clear()
   location.reload()
   ```
3. Close browser completely and restart
4. Verify frontend container restarted:
   ```powershell
   docker restart erp_frontend
   docker logs erp_frontend --tail 20
   ```

### Issue 2: Dropdown Not Working
**Symptoms**: Click Production → Nothing happens
**Possible Causes**:
- Sidebar collapsed
- JavaScript error

**Solutions**:
1. Expand sidebar first (click hamburger icon)
2. Check browser console for errors
3. Verify React app loaded properly

### Issue 3: Login Not Redirecting
**Symptoms**: Login successful but stays on login page
**Possible Causes**:
- Backend not returning user data
- Frontend not updated

**Solutions**:
1. Check backend logs:
   ```powershell
   docker logs erp_backend --tail 30 | Select-String "login"
   ```
2. Verify AuthResponse schema:
   ```powershell
   docker exec erp_backend cat app/core/schemas.py | Select-String -Pattern "class AuthResponse" -Context 5
   ```
3. Restart backend:
   ```powershell
   docker restart erp_backend
   ```

### Issue 4: Pages Show Blank/Empty
**Symptoms**: Navigate to page → White screen
**Possible Causes**:
- Page import error
- Missing component

**Solutions**:
1. Check browser console for errors
2. Verify page file exists:
   ```powershell
   Get-ChildItem "erp-ui\frontend\src\pages\" -Filter "*.tsx"
   ```
3. Check frontend logs:
   ```powershell
   docker logs erp_frontend --tail 50
   ```

---

## 📊 Test Results Template

**Test Date**: _______________
**Tester**: _______________

| Test | Result | Notes |
|------|--------|-------|
| Auth Persistence (Refresh) | ⬜ Pass / ⬜ Fail | |
| Login Redirect | ⬜ Pass / ⬜ Fail | |
| Navbar Dropdown | ⬜ Pass / ⬜ Fail | |
| Sidebar Collapse | ⬜ Pass / ⬜ Fail | |
| Role-Based Access | ⬜ Pass / ⬜ Fail | |
| Dashboard Page | ⬜ Pass / ⬜ Fail | |
| PPIC Page | ⬜ Pass / ⬜ Fail | |
| Purchasing Page | ⬜ Pass / ⬜ Fail | |
| Cutting Page | ⬜ Pass / ⬜ Fail | |
| Embroidery Page | ⬜ Pass / ⬜ Fail | |
| Sewing Page | ⬜ Pass / ⬜ Fail | |
| Finishing Page | ⬜ Pass / ⬜ Fail | |
| Packing Page | ⬜ Pass / ⬜ Fail | |
| Warehouse Page | ⬜ Pass / ⬜ Fail | |
| Finish Goods Page | ⬜ Pass / ⬜ Fail | |
| QC Page | ⬜ Pass / ⬜ Fail | |
| Reports Page | ⬜ Pass / ⬜ Fail | |
| Admin Page | ⬜ Pass / ⬜ Fail | |

**Overall Result**: ⬜ All Pass / ⬜ Some Failures

**Failures Summary**:
```
(List any failures and error messages)
```

**Screenshots**:
```
(Attach screenshots of any issues)
```

---

## 🎯 Success Criteria

✅ **All Tests Must Pass**:
- [ ] Auth persistence working (no redirect on refresh)
- [ ] Login redirects to dashboard
- [ ] Navbar dropdown functions correctly
- [ ] All 15 pages load without errors
- [ ] Role-based access control working
- [ ] No JavaScript console errors
- [ ] Browser localStorage contains valid data

**When All Criteria Met**: ✅ System Ready for UAT

---

## 📞 Support

**If Issues Persist**:
1. Document the error (screenshot + console log)
2. Check Docker container status:
   ```powershell
   docker ps -a
   docker logs erp_backend --tail 50
   docker logs erp_frontend --tail 50
   ```
3. Restart all services:
   ```powershell
   docker-compose down
   docker-compose up -d
   ```
4. Contact: Daniel Rizaldy (Senior Developer)

---

**Document Version**: 1.0
**Last Updated**: January 20, 2026
