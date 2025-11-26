# Vehicle Parking Management System (VPMS) - Frontend

A professional, responsive frontend application for managing vehicle parking built with Vue 3, TypeScript, and Bootstrap 5.

## Features

### Admin Features
- **Dashboard**: View statistics, charts, and recent activity
- **Parking Lot Management**: Create, edit, and delete parking lots
- **Spot Management**: View and monitor parking spot status
- **User Management**: View all registered users and their statistics
- **Analytics**: Visual charts showing parking lot status and occupancy

### User Features
- **Dashboard**: Personal statistics and booking history
- **Book Parking**: Select and book available parking spots
- **My Bookings**: View and manage all bookings
- **Release Parking**: Vacate parking spots
- **Export CSV**: Download booking history as CSV
- **Charts**: Monthly booking trends and parking lot usage

## Tech Stack

- **Vue 3** with Composition API and TypeScript
- **Vue Router** for navigation
- **Pinia** for state management
- **Axios** for API communication
- **Bootstrap 5** for UI components and styling
- **Chart.js** for data visualization
- **Vite** for build tooling

## Project Structure

```
src/
├── components/       # Reusable components (Navbar, Footer)
├── views/           # Page components
│   ├── LoginView.vue
│   ├── RegisterView.vue
│   ├── AdminDashboard.vue
│   ├── AdminParkingLots.vue
│   ├── AdminUsers.vue
│   ├── UserDashboard.vue
│   ├── BookParkingView.vue
│   └── MyBookingsView.vue
├── router/          # Vue Router configuration
├── stores/          # Pinia stores (auth)
├── services/        # API service layer
├── App.vue          # Root component
├── main.ts          # Application entry point
└── style.css        # Global styles
```

## Setup Instructions

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

3. Update the API URL in `.env` if your Flask backend runs on a different port:
```
VITE_API_URL=http://localhost:5000/api
```

### Development

Run the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173` (or the port shown in terminal).

### Build for Production

Build the application:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

## API Integration

The frontend expects a Flask backend API with the following endpoints:

### Authentication
- `POST /api/user/register` - User registration
- `POST /api/user/login` - User login
- `POST /api/admin/login` - Admin login

### Admin Endpoints
- `GET /api/admin/stats` - Dashboard statistics
- `GET /api/admin/recent-activity` - Recent parking activity
- `GET /api/admin/parking-lots` - List all parking lots
- `POST /api/admin/parking-lots` - Create parking lot
- `PUT /api/admin/parking-lots/:id` - Update parking lot
- `DELETE /api/admin/parking-lots/:id` - Delete parking lot
- `GET /api/admin/parking-lots/:id/spots` - Get spots for a lot
- `GET /api/admin/users` - List all users

### User Endpoints
- `GET /api/user/stats` - User dashboard statistics
- `GET /api/user/active-booking` - Get active booking
- `GET /api/user/parking-lots/available` - Get available parking lots
- `POST /api/user/book-parking` - Book a parking spot
- `GET /api/user/bookings` - Get user bookings
- `POST /api/user/bookings/:id/release` - Release parking spot
- `GET /api/user/export-csv` - Export booking history

## Features Implemented

✅ Responsive design for mobile and desktop
✅ Role-based authentication (Admin/User)
✅ Form validation (frontend)
✅ Professional UI with Bootstrap 5
✅ Chart.js integration for analytics
✅ API service layer with interceptors
✅ State management with Pinia
✅ Protected routes with navigation guards
✅ Error handling and loading states
✅ Modal dialogs for confirmations
✅ CSV export functionality

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Notes

- The application uses Bootstrap 5 via CDN for styling
- Chart.js is used for data visualization
- All API calls are handled through the centralized API service
- Authentication tokens are stored in localStorage
- The app automatically redirects to login if token expires

## License

This project is part of an academic assignment.
