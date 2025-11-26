# 🚀 How to Start the Complete VPMS Project

## ✅ Backend Status: RUNNING
You're seeing the JSON response, which means the Flask backend is working perfectly!

## Next Steps:

### Step 1: Start the Frontend (Vue.js)

Open a **NEW terminal window** and run:

```bash
# Make sure you're in the project root (vpms folder)
cd C:\Users\adity\vpms

# Start the frontend development server
npm run dev
```

You should see:
```
  VITE v7.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Step 2: Open the Application

1. Open your browser
2. Go to: **http://localhost:5173**
3. You'll see the login page

### Step 3: Login as Admin

- Click on **"Admin Login"** tab
- Username: `admin`
- Password: `admin123`
- Click **Login**

## 📋 Complete Setup Checklist

### Terminal 1: Backend (Flask) ✅
```bash
cd backend
python run.py
# Should show: Running on http://127.0.0.1:5000
```

### Terminal 2: Frontend (Vue.js) ⏳
```bash
cd C:\Users\adity\vpms
npm run dev
# Should show: Local: http://localhost:5173/
```

### Terminal 3: Redis (Optional - for caching)
```bash
redis-server
```

### Terminal 4: Celery Worker (Optional - for background jobs)
```bash
cd backend
celery -A tasks.celery_app:celery_app worker --loglevel=info --pool=solo
```

## 🎯 Quick Test

1. **Backend running?** ✅ (You see the JSON)
2. **Frontend running?** → Start with `npm run dev`
3. **Open browser:** http://localhost:5173
4. **Login:** admin / admin123

## 🔍 Troubleshooting

### Frontend won't start?
```bash
# Make sure dependencies are installed
npm install

# Then start
npm run dev
```

### Can't login?
- Make sure backend is running on port 5000
- Check browser console for errors (F12)
- Verify admin user exists (should be created automatically)

### API connection errors?
- Backend must be running on `http://localhost:5000`
- Frontend expects API at `http://localhost:5000/api`
- Check `.env` file if you have one (optional)

## 📝 Summary

**What you have:**
- ✅ Backend API running (Flask on port 5000)
- ✅ Database created
- ✅ Admin user created (admin/admin123)

**What you need:**
- ⏳ Frontend running (Vue.js on port 5173)
- ⏳ Browser open to http://localhost:5173

**Next command to run:**
```bash
npm run dev
```



