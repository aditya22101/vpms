from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)  # 'admin' or 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'
    
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)  # Price per hour
    number_of_spots = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    spots = db.relationship('ParkingSpot', backref='parking_lot', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        available_spots = len([s for s in self.spots if s.status == 'A'])
        return {
            'id': self.id,
            'prime_location_name': self.prime_location_name,
            'address': self.address,
            'pin_code': self.pin_code,
            'price': self.price,
            'number_of_spots': self.number_of_spots,
            'available_spots': available_spots,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'
    
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    status = db.Column(db.String(1), default='A', nullable=False)  # 'A' for Available, 'O' for Occupied
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='parking_spot', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'lot_id': self.lot_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost = db.Column(db.Float, default=0.0)
    remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def calculate_cost(self, price_per_hour):
        """Calculate parking cost based on time"""
        if not self.leaving_timestamp:
            return 0.0
        duration = (self.leaving_timestamp - self.parking_timestamp).total_seconds() / 3600  # hours
        return round(duration * price_per_hour, 2)
    
    def to_dict(self):
        return {
            'id': self.id,
            'spot_id': self.spot_id,
            'user_id': self.user_id,
            'parking_timestamp': self.parking_timestamp.isoformat() if self.parking_timestamp else None,
            'leaving_timestamp': self.leaving_timestamp.isoformat() if self.leaving_timestamp else None,
            'parking_cost': self.parking_cost,
            'remarks': self.remarks,
            'status': 'active' if not self.leaving_timestamp else 'completed',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }



