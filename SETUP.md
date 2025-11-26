# VPMS Frontend Setup Guide

## Quick Start

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Configure Environment**
   - Copy `.env.example` to `.env` (if not exists)
   - Update `VITE_API_URL` to match your Flask backend URL
   - Default: `http://localhost:5000/api`

3. **Start Development Server**
   ```bash
   npm run dev
   ```

4. **Access the Application**
   - Open browser to `http://localhost:5173` (or port shown in terminal)

## Project Structure

```
vpms/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Navbar.vue      # Navigation bar
│   │   └── Footer.vue      # Footer component
│   ├── views/              # Page components
│   │   ├── LoginView.vue
│   │   ├── RegisterView.vue
│   │   ├── AdminDashboard.vue
│   │   ├── AdminParkingLots.vue
│   │   ├── AdminUsers.vue
│   │   ├── UserDashboard.vue
│   │   ├── BookParkingView.vue
│   │   └── MyBookingsView.vue
│   ├── router/             # Vue Router configuration
│   │   └── index.ts
│   ├── stores/             # Pinia state management
│   │   └── auth.ts        # Authentication store
│   ├── services/           # API services
│   │   └── api.ts         # Axios instance with interceptors
│   ├── utils/             # Utility functions
│   │   └── chart.ts       # Chart.js setup
│   ├── App.vue            # Root component
│   ├── main.ts            # Application entry
│   └── style.css          # Global styles
├── index.html             # HTML template
├── package.json           # Dependencies
└── vite.config.ts         # Vite configuration
```

## Key Features

### Authentication
- **Login**: Separate login for Admin and User
- **Register**: User registration with validation
- **Protected Routes**: Role-based access control
- **Token Management**: JWT token stored in localStorage

### Admin Features
- Dashboard with statistics and charts
- Create/Edit/Delete parking lots
- View parking spot status
- Manage users
- View analytics

### User Features
- Personal dashboard
- Book parking spots (auto-allocation)
- View booking history
- Release parking spots
- Export booking history as CSV
- View personal analytics

## API Integration

The frontend expects the following API structure:

### Base URL
Configured in `.env` file as `VITE_API_URL`

### Authentication Endpoints
- `POST /api/user/register` - Register new user
- `POST /api/user/login` - User login
- `POST /api/admin/login` - Admin login

### Response Format
```json
{
  "token": "jwt_token_here",
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com"
  }
}
```

### Error Format
```json
{
  "message": "Error message here"
}
```

## Styling

- **Bootstrap 5**: Loaded via CDN in `index.html`
- **Bootstrap Icons**: Included for icons
- **Custom CSS**: Global styles in `src/style.css`
- **Responsive**: Mobile-first design

## State Management

Using Pinia for:
- Authentication state (user, token, role)
- Login/logout actions
- User data persistence

## Routing

Protected routes with navigation guards:
- `/login` - Public
- `/register` - Public
- `/admin/*` - Requires admin role
- `/user/*` - Requires user role

## Development Tips

1. **API Errors**: Check browser console and network tab
2. **TypeScript Errors**: Run `npm run build` to check types
3. **Hot Reload**: Changes auto-reload in dev mode
4. **Environment Variables**: Must start with `VITE_` to be accessible

## Build for Production

```bash
npm run build
```

Output will be in `dist/` directory.

## Testing the Frontend

Even without a backend, you can:
1. View all UI components
2. Test form validation
3. Navigate between pages
4. See demo data in components

For full functionality, connect to Flask backend API.

