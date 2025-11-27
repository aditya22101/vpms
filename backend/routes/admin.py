from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from database import User, ParkingLot, ParkingSpot, Reservation, db
from extensions import redis_client, REDIS_AVAILABLE
from datetime import datetime, timedelta
from utils.decorators import admin_required
from utils.cache import cache_response, get_cached, set_cached
import traceback

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_stats():
    """Get admin dashboard statistics"""
    try:
        # Try to get from cache
        cache_key = 'admin_stats'
        cached = get_cached(cache_key)
        if cached:
            return jsonify(cached), 200
        
        # Get statistics from database
        total_lots = ParkingLot.query.count()
        total_spots = ParkingSpot.query.count()
        occupied_spots = ParkingSpot.query.filter_by(status='O').count()
        available_spots = ParkingSpot.query.filter_by(status='A').count()
        total_users = User.query.filter_by(role='user').count()
        active_reservations = Reservation.query.filter_by(leaving_timestamp=None).count()
        
        stats = {
            'totalLots': total_lots,
            'totalSpots': total_spots,
            'occupiedSpots': occupied_spots,
            'availableSpots': available_spots,
            'totalUsers': total_users,
            'activeReservations': active_reservations
        }
        
        # Cache for 5 minutes
        set_cached(cache_key, stats, timeout=300)
        
        return jsonify(stats), 200
    except Exception as e:
        print(f"Error in get_stats: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'message': f'Error fetching stats: {str(e)}'}), 500

@admin_bp.route('/recent-activity', methods=['GET'])
@jwt_required()
@admin_required
def get_recent_activity():
    """Get recent parking activity"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        reservations = Reservation.query.order_by(
            Reservation.parking_timestamp.desc()
        ).limit(limit).all()
        
        activity = []
        for res in reservations:
            spot = ParkingSpot.query.get(res.spot_id)
            lot = ParkingLot.query.get(spot.lot_id) if spot else None
            user = User.query.get(res.user_id)
            
            activity.append({
                'id': res.id,
                'username': user.username if user else 'Unknown',
                'lot_name': lot.prime_location_name if lot else 'Unknown',
                'spot_id': res.spot_id,
                'status': 'O' if not res.leaving_timestamp else 'A',
                'parking_timestamp': res.parking_timestamp.isoformat() if res.parking_timestamp else None,
                'leaving_timestamp': res.leaving_timestamp.isoformat() if res.leaving_timestamp else None,
                'cost': res.parking_cost
            })
        
        return jsonify(activity), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching activity: {str(e)}'}), 500

@admin_bp.route('/parking-lots', methods=['GET'])
@jwt_required()
@admin_required
def get_parking_lots():
    """Get all parking lots"""
    try:
        # Try to get from cache
        cache_key = 'all_parking_lots'
        cached = get_cached(cache_key)
        if cached:
            return jsonify(cached), 200

        lots = ParkingLot.query.all()
        result = [lot.to_dict() for lot in lots]

        # Cache for 10 minutes (parking lots don't change often)
        set_cached(cache_key, result, timeout=600)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching parking lots: {str(e)}'}), 500

@admin_bp.route('/parking-lots', methods=['POST'])
@jwt_required()
@admin_required
def create_parking_lot():
    """Create a new parking lot"""
    try:
        data = request.get_json() or {}

        # Validation
        required_fields = ['prime_location_name', 'address', 'pin_code', 'price', 'number_of_spots']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400

        # Validate & convert numeric fields
        try:
            price = float(data['price'])
            number_of_spots = int(data['number_of_spots'])
        except ValueError:
            return jsonify({'message': 'Invalid numeric value for price or number_of_spots'}), 400

        # Create parking lot
        lot = ParkingLot(
            prime_location_name=data['prime_location_name'],
            address=data['address'],
            pin_code=data['pin_code'],
            price=price,
            number_of_spots=number_of_spots
        )

        # Set updated timestamp
        lot.updated_at = datetime.utcnow()

        db.session.add(lot)
        db.session.flush()  # Get lot ID

        # Create parking spots
        for i in range(lot.number_of_spots):
            spot = ParkingSpot(
                lot_id=lot.id,
                status='A'
            )
            db.session.add(spot)

        db.session.commit()

        # Clear cache
        try:
            if redis_client:
                redis_client.delete('admin_stats')
                redis_client.delete('all_parking_lots')
                redis_client.delete('available_lots')
        except Exception:
            pass

        print(f"✅ Created parking lot '{lot.prime_location_name}' with {lot.number_of_spots} spots")
        return jsonify(lot.to_dict()), 201

    except Exception as e:
        print(f"❌ Error in create_parking_lot: {str(e)}")
        print(traceback.format_exc())
        db.session.rollback()
        return jsonify({'message': f'Error creating parking lot: {str(e)}'}), 500


@admin_bp.route('/parking-lots/<int:lot_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_parking_lot(lot_id):
    """Update a parking lot"""
    try:
        lot = ParkingLot.query.get_or_404(lot_id)
        data = request.get_json() or {}

        # Update simple fields
        if 'prime_location_name' in data:
            lot.prime_location_name = data['prime_location_name']

        if 'address' in data:
            lot.address = data['address']

        if 'pin_code' in data:
            lot.pin_code = data['pin_code']

        # Validate & update price
        if 'price' in data:
            try:
                lot.price = float(data['price'])
                if lot.price < 0:
                    return jsonify({"message": "Price cannot be negative"}), 400
            except ValueError:
                return jsonify({"message": "Invalid price value"}), 400

        # Handle change in number_of_spots
        if 'number_of_spots' in data:
            try:
                new_count = int(data['number_of_spots'])
                if new_count < 0:
                    return jsonify({"message": "number_of_spots cannot be negative"}), 400
            except ValueError:
                return jsonify({"message": "Invalid number_of_spots"}), 400

            current_count = len(lot.spots)

            if new_count > current_count:
                # Add new spots
                for _ in range(new_count - current_count):
                    db.session.add(ParkingSpot(lot_id=lot.id, status='A'))

            elif new_count < current_count:
                # Only remove available spots
                available_spots = [s for s in lot.spots if s.status == 'A']
                remove_count = current_count - new_count

                if len(available_spots) < remove_count:
                    return jsonify({'message': 'Cannot reduce spots. Some spots are occupied.'}), 400

                for spot in available_spots[:remove_count]:
                    db.session.delete(spot)

            lot.number_of_spots = new_count

        # Update timestamp
        try:
            lot.updated_at = datetime.utcnow()
        except:
            pass  # in case model doesn't have the field

        db.session.commit()

        # Clear cache
        if redis_client:
            try:
                redis_client.delete('admin_stats')
                redis_client.delete('all_parking_lots')
                redis_client.delete('available_lots')
                redis_client.delete(f'lot_{lot_id}_spots')
            except:
                pass

        return jsonify(lot.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        print("❌ Error updating parking lot:", str(e))
        return jsonify({'message': f'Error updating parking lot: {str(e)}'}), 500

@admin_bp.route('/parking-lots/<int:lot_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_parking_lot(lot_id):
    """Delete a parking lot (only if all spots are empty)"""
    try:
        lot = ParkingLot.query.get_or_404(lot_id)
        
        # Check if any spots are occupied
        occupied_spots = ParkingSpot.query.filter_by(lot_id=lot_id, status='O').count()
        if occupied_spots > 0:
            return jsonify({'message': 'Cannot delete parking lot. Some spots are occupied.'}), 400
        
        db.session.delete(lot)
        db.session.commit()
        
        # Clear cache
        try:
            if redis_client:
                redis_client.delete('admin_stats')
                redis_client.delete('all_parking_lots')
                redis_client.delete('available_lots')
                redis_client.delete(f'lot_{lot_id}_spots')
        except Exception:
            pass

        return jsonify({'message': 'Parking lot deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error deleting parking lot: {str(e)}'}), 500

@admin_bp.route('/parking-lots/<int:lot_id>/spots', methods=['GET'])
@jwt_required()
@admin_required
def get_parking_spots(lot_id):
    """Get all spots for a parking lot"""
    try:
        # Try to get from cache
        cache_key = f'lot_{lot_id}_spots'
        cached = get_cached(cache_key)
        if cached:
            return jsonify(cached), 200

        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        result = [spot.to_dict() for spot in spots]

        # Cache for 2 minutes (spot status changes on bookings)
        set_cached(cache_key, result, timeout=120)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching spots: {str(e)}'}), 500

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    """Get all users"""
    try:
        # Try to get from cache
        cache_key = 'all_users_with_stats'
        cached = get_cached(cache_key)
        if cached:
            return jsonify(cached), 200

        users = User.query.filter_by(role='user').all()

        user_list = []
        for user in users:
            total_bookings = Reservation.query.filter_by(user_id=user.id).count()
            active_bookings = Reservation.query.filter_by(
                user_id=user.id,
                leaving_timestamp=None
            ).count()

            total_spent = db.session.query(
                db.func.sum(Reservation.parking_cost)
            ).filter_by(user_id=user.id).scalar() or 0

            user_data = user.to_dict()
            user_data.update({
                'total_bookings': total_bookings,
                'active_bookings': active_bookings,
                'total_spent': round(total_spent, 2)
            })
            user_list.append(user_data)

        # Cache for 5 minutes (user list changes rarely)
        set_cached(cache_key, user_list, timeout=300)

        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching users: {str(e)}'}), 500

