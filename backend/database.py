"""
Database Configuration and Models for VPMS
SQLite Database with Flask-SQLAlchemy
"""
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy
db = SQLAlchemy()

# Database Configuration
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'vpms.db')
DATABASE_URI = f'sqlite:///{DATABASE_PATH}'

def init_db(app):
    """
    Initialize database with Flask app
    Creates all tables and sets up database
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False  # Set to True for SQL query logging
    
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print(f"✅ Database initialized: {DATABASE_PATH}")
        print(f"✅ All tables created successfully")
    
    return db

def reset_db(app):
    """
    Reset database - DROP ALL TABLES and recreate
    WARNING: This will delete all data!
    """
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("✅ Database reset complete")

# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(db.Model):
    """
    User Model - Stores admin and regular users
    """
    __tablename__ = 'users'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # User Information
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Role: 'admin' or 'user'
    role = db.Column(db.String(20), default='user', nullable=False, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class ParkingLot(db.Model):
    """
    Parking Lot Model - Stores parking lot information
    """
    __tablename__ = 'parking_lots'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Location Information
    prime_location_name = db.Column(db.String(200), nullable=False, index=True)
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(10), nullable=False, index=True)
    
    # Pricing
    price = db.Column(db.Float, nullable=False)  # Price per hour
    
    # Capacity
    number_of_spots = db.Column(db.Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    spots = db.relationship('ParkingSpot', backref='parking_lot', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary with available spots count"""
        available_spots = len([s for s in self.spots if s.status == 'A'])
        occupied_spots = len([s for s in self.spots if s.status == 'O'])
        
        return {
            'id': self.id,
            'prime_location_name': self.prime_location_name,
            'address': self.address,
            'pin_code': self.pin_code,
            'price': self.price,
            'number_of_spots': self.number_of_spots,
            'available_spots': available_spots,
            'occupied_spots': occupied_spots,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ParkingLot {self.prime_location_name}>'


class ParkingSpot(db.Model):
    """
    Parking Spot Model - Individual parking spots within a lot
    """
    __tablename__ = 'parking_spots'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Status: 'A' = Available, 'O' = Occupied
    status = db.Column(db.String(1), default='A', nullable=False, index=True)
    
    # Spot Information (optional)
    spot_number = db.Column(db.String(20), nullable=True)  # e.g., "A-01", "B-05"
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='parking_spot', lazy=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'lot_id': self.lot_id,
            'status': self.status,
            'spot_number': self.spot_number,
            'status_text': 'Available' if self.status == 'A' else 'Occupied',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ParkingSpot {self.id} - Lot {self.lot_id} - {self.status}>'


class Reservation(db.Model):
    """
    Reservation Model - Stores parking bookings/reservations
    """
    __tablename__ = 'reservations'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Timestamps
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    leaving_timestamp = db.Column(db.DateTime, nullable=True, index=True)
    
    # Cost Information
    parking_cost = db.Column(db.Float, default=0.0, nullable=False)
    price_per_hour = db.Column(db.Float, nullable=True)  # Store price at time of booking
    
    # Additional Information
    remarks = db.Column(db.Text, nullable=True)
    vehicle_number = db.Column(db.String(20), nullable=True)  # Vehicle registration number
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_cost(self, price_per_hour=None):
        """
        Calculate parking cost based on time
        Uses provided price_per_hour or stored price_per_hour
        """
        if not self.leaving_timestamp:
            return 0.0
        
        price = price_per_hour or self.price_per_hour or 0.0
        if price == 0.0:
            return 0.0
        
        # Calculate duration in hours
        duration = (self.leaving_timestamp - self.parking_timestamp).total_seconds() / 3600
        
        # Round up to nearest hour (minimum 1 hour)
        hours = max(1, int(duration) + (1 if duration % 1 > 0 else 0))
        
        return round(hours * price, 2)
    
    def get_duration_hours(self):
        """Get parking duration in hours"""
        if not self.leaving_timestamp:
            # Calculate from parking time to now
            duration = (datetime.utcnow() - self.parking_timestamp).total_seconds() / 3600
        else:
            duration = (self.leaving_timestamp - self.parking_timestamp).total_seconds() / 3600
        return round(duration, 2)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'spot_id': self.spot_id,
            'user_id': self.user_id,
            'parking_timestamp': self.parking_timestamp.isoformat() if self.parking_timestamp else None,
            'leaving_timestamp': self.leaving_timestamp.isoformat() if self.leaving_timestamp else None,
            'parking_cost': self.parking_cost,
            'price_per_hour': self.price_per_hour,
            'remarks': self.remarks,
            'vehicle_number': self.vehicle_number,
            'duration_hours': self.get_duration_hours(),
            'status': 'active' if not self.leaving_timestamp else 'completed',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Reservation {self.id} - User {self.user_id} - Spot {self.spot_id}>'


# ============================================================================
# DATABASE UTILITIES
# ============================================================================

def create_admin_user():
    """
    Create default admin user if it doesn't exist
    """
    admin = User.query.filter_by(username='admin', role='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@vpms.com',
            role='admin'
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        
        print("=" * 60)
        print("✅ Admin user created successfully!")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print("=" * 60)
        return admin
    else:
        print("ℹ️  Admin user already exists")
        return admin

def get_db_stats():
    """
    Get database statistics
    """
    stats = {
        'users': User.query.count(),
        'parking_lots': ParkingLot.query.count(),
        'parking_spots': ParkingSpot.query.count(),
        'reservations': Reservation.query.count(),
        'available_spots': ParkingSpot.query.filter_by(status='A').count(),
        'occupied_spots': ParkingSpot.query.filter_by(status='O').count(),
        'active_reservations': Reservation.query.filter_by(leaving_timestamp=None).count()
    }
    return stats

def check_db_connection():
    """
    Check if database connection is working
    """
    try:
        db.session.execute(db.text('SELECT 1'))
        return True
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        return False

# Export all models
__all__ = [
    'db',
    'init_db',
    'reset_db',
    'User',
    'ParkingLot',
    'ParkingSpot',
    'Reservation',
    'create_admin_user',
    'get_db_stats',
    'check_db_connection',
    'DATABASE_URI',
    'DATABASE_PATH'
]

