# VPMS Backend - Flask API

Backend API for Vehicle Parking Management System built with Flask, SQLite, Redis, and Celery.

## Tech Stack

- **Flask** - Web framework
- **SQLite** - Database
- **Redis** - Caching and message broker
- **Celery** - Asynchronous task processing
- **Flask-JWT-Extended** - JWT authentication
- **Flask-CORS** - Cross-origin resource sharing

## Features

### Authentication
- User registration and login
- Admin login (default: admin/admin123)
- JWT token-based authentication

### Admin Endpoints
- Dashboard statistics
- Parking lot management (CRUD)
- Parking spot management
- User management
- Recent activity tracking

### User Endpoints
- Dashboard statistics
- Book parking spots (auto-allocation)
- Release parking spots
- View booking history
- Export booking history as CSV

### Background Jobs (Celery)
- **Daily Reminders**: Sent at 6 PM every day to users who haven't booked recently
- **Monthly Reports**: Sent on the 1st of every month with activity summary
- **CSV Export**: Async export of booking history

## Setup Instructions

### Prerequisites
- Python 3.8+
- Redis server
- pip

### Installation

1. **Install Python dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Install and start Redis:**

**Windows:**
- Download Redis from: https://github.com/microsoftarchive/redis/releases
- Or use WSL: `sudo apt-get install redis-server`
- Start Redis: `redis-server`

**Linux/Mac:**
```bash
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis  # Mac
redis-server
```

3. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Initialize the database:**
```bash
python app.py
```

This will:
- Create the database file (`vpms.db`)
- Create all tables
- Create admin user (username: `admin`, password: `admin123`)

### Running the Application

1. **Start Flask server:**
```bash
python app.py
```

The API will be available at `http://localhost:5000`

2. **Start Celery worker (in a separate terminal):**
```bash
celery -A tasks.celery_app:celery_app worker --loglevel=info
```

3. **Start Celery beat scheduler (in another terminal):**
```bash
celery -A tasks.celery_app:celery_app beat --loglevel=info
```

## API Endpoints

### Authentication
- `POST /api/user/register` - Register new user
- `POST /api/user/login` - User login
- `POST /api/admin/login` - Admin login

### Admin Endpoints (require admin token)
- `GET /api/admin/stats` - Dashboard statistics
- `GET /api/admin/recent-activity` - Recent parking activity
- `GET /api/admin/parking-lots` - List all parking lots
- `POST /api/admin/parking-lots` - Create parking lot
- `PUT /api/admin/parking-lots/:id` - Update parking lot
- `DELETE /api/admin/parking-lots/:id` - Delete parking lot
- `GET /api/admin/parking-lots/:id/spots` - Get spots for a lot
- `GET /api/admin/users` - List all users

### User Endpoints (require user token)
- `GET /api/user/stats` - User dashboard statistics
- `GET /api/user/active-booking` - Get active booking
- `GET /api/user/parking-lots/available` - Get available parking lots
- `POST /api/user/book-parking` - Book a parking spot
- `GET /api/user/bookings` - Get user bookings
- `POST /api/user/bookings/:id/release` - Release parking spot
- `GET /api/user/export-csv` - Export booking history (async)

## Default Admin Credentials

- **Username:** `admin`
- **Password:** `admin123`

⚠️ **Change these in production!**

## Database Schema

### Users
- id, username, email, password_hash, role, created_at

### Parking Lots
- id, prime_location_name, address, pin_code, price, number_of_spots, created_at, updated_at

### Parking Spots
- id, lot_id, status (A/O), created_at

### Reservations
- id, spot_id, user_id, parking_timestamp, leaving_timestamp, parking_cost, remarks, created_at

## Caching

Redis is used for:
- Dashboard statistics (5 min cache)
- Available parking lots (1 min cache)
- User statistics (2 min cache)

## Background Jobs

### Daily Reminders
- Runs every day at 6 PM
- Sends reminders to users who haven't booked in 7+ days
- Uses Google Chat Webhook (configure in .env)

### Monthly Reports
- Runs on the 1st of every month at 9 AM
- Generates HTML report with:
  - Total bookings
  - Total amount spent
  - Most used parking lot
- Email functionality can be added

### CSV Export
- Triggered by user request
- Generates CSV with booking history
- Returns task ID for status tracking

## Development

### Project Structure
```
backend/
├── app.py                 # Flask application entry point
├── config.py              # Configuration
├── models.py              # Database models
├── extensions.py          # Flask extensions
├── requirements.txt       # Python dependencies
├── routes/
│   ├── auth.py           # Authentication routes
│   ├── admin.py          # Admin routes
│   └── user.py           # User routes
├── tasks/
│   ├── celery_app.py     # Celery configuration
│   ├── scheduled_tasks.py # Scheduled tasks
│   └── export_tasks.py   # CSV export task
└── utils/
    ├── decorators.py     # Custom decorators
    └── cache.py          # Cache utilities
```

## Testing

Test the API using curl or Postman:

```bash
# Register user
curl -X POST http://localhost:5000/api/user/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"test123"}'

# Login
curl -X POST http://localhost:5000/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'

# Admin login
curl -X POST http://localhost:5000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## Notes

- Database is created automatically on first run
- Admin user is created automatically with default credentials
- Redis must be running for caching and Celery
- Celery worker and beat must be running for background jobs
- CORS is enabled for all origins (configure in production)

## Troubleshooting

1. **Redis connection error**: Make sure Redis is running
2. **Database errors**: Delete `vpms.db` and restart to recreate
3. **Celery tasks not running**: Check Celery worker and beat are running
4. **Import errors**: Make sure all dependencies are installed



