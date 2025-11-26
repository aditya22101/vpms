# Fix Database Issues - Step by Step Guide

## Quick Fix Steps

### Step 1: Delete Old Database
```bash
cd backend
del vpms.db  # Windows
# or
rm vpms.db   # Linux/Mac
```

### Step 2: Verify Database Setup
```bash
python verify_database.py
```

This will:
- ✅ Test database connection
- ✅ Check all tables exist
- ✅ Verify admin user
- ✅ Test creating parking lots
- ✅ Test booking functionality
- ✅ Test release functionality
- ✅ Test statistics

### Step 3: If Tests Fail

**Error: "Database connection failed"**
- Check file permissions
- Ensure you're in the backend directory
- Try running as administrator

**Error: "Tables missing"**
- Restart the backend: `python run.py`
- Tables are created automatically on startup

**Error: "Admin user not found"**
- Admin is created automatically
- If it fails, check console for errors

### Step 4: Test API Endpoints

**Test Admin Login:**
```bash
curl -X POST http://localhost:5000/api/admin/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

**Test Create Parking Lot (after login, use token):**
```bash
curl -X POST http://localhost:5000/api/admin/parking-lots ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer YOUR_TOKEN" ^
  -d "{\"prime_location_name\":\"Test Lot\",\"address\":\"123 Test St\",\"pin_code\":\"123456\",\"price\":50,\"number_of_spots\":10}"
```

## Common Issues and Solutions

### Issue 1: "Failed to save parking lots"
**Cause:** Database not initialized or connection error

**Solution:**
1. Check backend console for errors
2. Verify database file exists: `dir backend\vpms.db`
3. Run verification: `python verify_database.py`
4. Restart backend: `python run.py`

### Issue 2: "Unable to book parking"
**Cause:** No parking lots created or no available spots

**Solution:**
1. Admin must create parking lots first
2. Ensure parking lot has `number_of_spots > 0`
3. Check spots were created: Use admin dashboard

### Issue 3: "Dashboard shows no data"
**Cause:** No data in database

**Solution:**
1. Create parking lots as admin
2. Create some bookings
3. Refresh dashboard

### Issue 4: "Database locked" or "Database is locked"
**Cause:** Multiple processes accessing database

**Solution:**
1. Close all backend instances
2. Delete `vpms.db` and restart
3. Ensure only one backend instance is running

## Verification Checklist

- [ ] Database file exists: `backend/vpms.db`
- [ ] Backend starts without errors
- [ ] Admin user can login
- [ ] Can create parking lots
- [ ] Parking spots are created automatically
- [ ] Can view parking lots in admin dashboard
- [ ] Can book parking spots as user
- [ ] Can release parking spots
- [ ] Statistics show correct data

## Testing Commands

```bash
# 1. Verify database
python backend/verify_database.py

# 2. Test API (if you have requests installed)
python backend/debug_routes.py

# 3. Check database file
dir backend\vpms.db  # Windows
ls -lh backend/vpms.db  # Linux/Mac
```

## Still Not Working?

1. **Check backend console** - Look for error messages
2. **Check browser console** (F12) - Look for API errors
3. **Check Network tab** (F12) - See API request/response
4. **Run verification script** - `python verify_database.py`
5. **Check database file** - Ensure it exists and has data

## Database File Location

The database is at:
```
backend/vpms.db
```

You can:
- View with DB Browser for SQLite
- Delete to reset (will be recreated)
- Backup by copying the file

