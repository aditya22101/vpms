from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db, User, ParkingLot, ParkingSpot, Reservation
from extensions import redis_client, REDIS_AVAILABLE
from datetime import datetime
from utils.decorators import user_required
from utils.cache import get_cached, set_cached
import traceback

try:
    from tasks.celery_app import celery_app
    from tasks.export_tasks import export_user_csv_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    print("Warning: Celery not available. CSV export will not work.")

user_bp = Blueprint('user', __name__)

# ----------------- USER STATS -----------------
@user_bp.route('/stats', methods=['GET'])
@jwt_required()
@user_required
def get_user_stats():
    try:
        user_id = int(get_jwt_identity())
        cache_key = f'user_stats_{user_id}'
        cached = get_cached(cache_key) if REDIS_AVAILABLE else None

        if cached:
            return jsonify(cached), 200

        total_bookings = Reservation.query.filter_by(user_id=user_id).count()
        active_bookings = Reservation.query.filter_by(
            user_id=user_id,
            leaving_timestamp=None
        ).count()

        total_spent = db.session.query(
            db.func.sum(Reservation.parking_cost)
        ).filter_by(user_id=user_id).scalar() or 0

        start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_bookings = Reservation.query.filter(
            Reservation.user_id == user_id,
            Reservation.parking_timestamp >= start_of_month
        ).count()

        stats = {
            'totalBookings': total_bookings,
            'activeBookings': active_bookings,
            'totalSpent': round(total_spent, 2),
            'monthlyBookings': monthly_bookings
        }

        if REDIS_AVAILABLE:
            set_cached(cache_key, stats, timeout=120)

        return jsonify(stats), 200

    except Exception as e:
        return jsonify({'message': f'Error fetching stats: {str(e)}'}), 500


# ----------------- ACTIVE BOOKING -----------------
@user_bp.route('/active-booking', methods=['GET'])
@jwt_required()
@user_required
def get_active_booking():
    try:
        user_id = int(get_jwt_identity())
        reservation = Reservation.query.filter_by(user_id=user_id, leaving_timestamp=None).first()

        if not reservation:
            return jsonify(None), 200

        spot = ParkingSpot.query.get(reservation.spot_id)
        lot = ParkingLot.query.get(spot.lot_id) if spot else None

        booking_data = reservation.to_dict()
        booking_data.update({
            'lot_name': lot.prime_location_name if lot else 'Unknown',
            'address': lot.address if lot else 'Unknown'
        })

        return jsonify(booking_data), 200

    except Exception as e:
        return jsonify({'message': f'Error fetching active booking: {str(e)}'}), 500


# ----------------- AVAILABLE PARKING LOTS -----------------
@user_bp.route('/parking-lots/available', methods=['GET'])
@jwt_required()
@user_required
def get_available_parking_lots():
    try:
        cache_key = 'available_lots'
        cached = get_cached(cache_key) if REDIS_AVAILABLE else None

        if cached:
            return jsonify(cached), 200

        lots = ParkingLot.query.all()
        available_lots = []

        for lot in lots:
            available_spots_count = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count()
            if available_spots_count > 0:
                lot_dict = lot.to_dict()
                lot_dict['available_spots'] = available_spots_count
                available_lots.append(lot_dict)

        if REDIS_AVAILABLE:
            set_cached(cache_key, available_lots, timeout=60)

        return jsonify(available_lots), 200

    except Exception as e:
        return jsonify({'message': f'Error fetching available lots: {str(e)}'}), 500


# ----------------- BOOK PARKING -----------------
@user_bp.route('/book-parking', methods=['POST'])
@jwt_required()
@user_required
def book_parking():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        if not data:
            return jsonify({'message': 'Request body is required'}), 400

        lot_id = data.get('lot_id')
        if not lot_id:
            return jsonify({'message': 'lot_id is required'}), 400

        try:
            lot_id = int(lot_id)
        except (ValueError, TypeError):
            return jsonify({'message': 'lot_id must be a valid integer'}), 400

        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return jsonify({'message': 'Parking lot not found'}), 404

        active_booking = Reservation.query.filter_by(user_id=user_id, leaving_timestamp=None).first()
        if active_booking:
            return jsonify({'message': 'You already have an active booking. Please release it before booking a new spot.'}), 400

        available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
        if not available_spot:
            return jsonify({'message': 'No available spots in this parking lot. Please try another lot.'}), 400

        reservation = Reservation(
            spot_id=available_spot.id,
            user_id=user_id,
            parking_timestamp=datetime.utcnow()
        )

        available_spot.status = 'O'

        db.session.add(reservation)
        db.session.commit()

        if redis_client:
            redis_client.delete('available_lots')
            redis_client.delete(f'user_stats_{user_id}')
            redis_client.delete(f'user_{user_id}_bookings')
            redis_client.delete('admin_stats')
            redis_client.delete(f'lot_{lot.id}_spots')
            redis_client.delete('all_users_with_stats')

        booking_data = reservation.to_dict()
        booking_data.update({
            'lot_name': lot.prime_location_name,
            'address': lot.address,
            'price': lot.price,
            'spot_number': available_spot.id
        })

        print(f"✅ User {user_id} booked spot {available_spot.id} in lot {lot_id}")
        return jsonify(booking_data), 201

    except Exception as e:
        print(f"❌ Error in book_parking: {str(e)}")
        print(traceback.format_exc())
        db.session.rollback()
        return jsonify({'message': f'Error booking parking: {str(e)}'}), 500


# ----------------- GET USER BOOKINGS -----------------
@user_bp.route('/bookings', methods=['GET'])
@jwt_required()
@user_required
def get_user_bookings():
    try:
        user_id = int(get_jwt_identity())

        # Try to get from cache
        cache_key = f'user_{user_id}_bookings'
        cached = get_cached(cache_key) if REDIS_AVAILABLE else None
        if cached:
            return jsonify(cached), 200

        reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.parking_timestamp.desc()).all()

        bookings = []
        for res in reservations:
            spot = ParkingSpot.query.get(res.spot_id)
            lot = ParkingLot.query.get(spot.lot_id) if spot else None
            booking_data = res.to_dict()
            booking_data.update({
                'lot_name': lot.prime_location_name if lot else 'Unknown',
                'address': lot.address if lot else 'Unknown'
            })
            bookings.append(booking_data)

        # Cache for 2 minutes (changes when user books/releases)
        if REDIS_AVAILABLE:
            set_cached(cache_key, bookings, timeout=120)

        return jsonify(bookings), 200

    except Exception as e:
        return jsonify({'message': f'Error fetching bookings: {str(e)}'}), 500


# ----------------- RELEASE PARKING -----------------
@user_bp.route('/bookings/<int:booking_id>/release', methods=['POST'])
@jwt_required()
@user_required
def release_parking(booking_id):
    try:
        user_id = int(get_jwt_identity())
        reservation = Reservation.query.filter_by(id=booking_id, user_id=user_id).first()

        if not reservation:
            return jsonify({'message': 'Booking not found or you do not have permission to release it'}), 404
        if reservation.leaving_timestamp:
            return jsonify({'message': 'Parking spot already released'}), 400

        spot = ParkingSpot.query.get(reservation.spot_id)
        lot = ParkingLot.query.get(spot.lot_id) if spot else None
        if not spot or not lot:
            return jsonify({'message': 'Parking spot or lot not found'}), 404

        reservation.leaving_timestamp = datetime.utcnow()
        reservation.parking_cost = reservation.calculate_cost(lot.price)

        spot.status = 'A'
        db.session.commit()

        if redis_client:
            redis_client.delete('available_lots')
            redis_client.delete(f'user_stats_{user_id}')
            redis_client.delete(f'user_{user_id}_bookings')
            redis_client.delete('admin_stats')
            redis_client.delete(f'lot_{lot.id}_spots')
            redis_client.delete('all_users_with_stats')

        reservation_data = reservation.to_dict()
        reservation_data['cost'] = reservation.parking_cost
        print(f"✅ User {user_id} released spot {spot.id}, cost: ₹{reservation.parking_cost}")
        return jsonify(reservation_data), 200

    except Exception as e:
        print(f"Error in release_parking: {str(e)}")
        print(traceback.format_exc())
        db.session.rollback()
        return jsonify({'message': f'Error releasing parking: {str(e)}'}), 500


# ----------------- EXPORT CSV (Immediate Download) -----------------
@user_bp.route('/export-csv', methods=['GET'])
@jwt_required()
@user_required
def export_csv():
    try:
        import csv
        import io

        user_id = int(get_jwt_identity())

        # Get user's reservations
        reservations = Reservation.query.filter_by(user_id=user_id).order_by(
            Reservation.parking_timestamp.desc()
        ).all()

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Reservation ID',
            'Spot ID',
            'Parking Lot',
            'Address',
            'Parking Timestamp',
            'Leaving Timestamp',
            'Duration (hours)',
            'Cost (₹)',
            'Status',
            'Remarks'
        ])

        # Write data
        for res in reservations:
            spot = ParkingSpot.query.get(res.spot_id)
            lot = ParkingLot.query.get(spot.lot_id) if spot else None

            writer.writerow([
                res.id,
                res.spot_id,
                lot.prime_location_name if lot else 'Unknown',
                lot.address if lot else 'Unknown',
                res.parking_timestamp.isoformat() if res.parking_timestamp else '',
                res.leaving_timestamp.isoformat() if res.leaving_timestamp else 'Active',
                res.get_duration_hours() if hasattr(res, 'get_duration_hours') else 0,
                res.parking_cost,
                'Active' if not res.leaving_timestamp else 'Completed',
                res.remarks or ''
            ])

        # Create response with CSV file
        output.seek(0)
        filename = f'parking-history-{user_id}-{datetime.now().strftime("%Y%m%d")}.csv'

        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        print(f"Error in export_csv: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'message': f'Error exporting CSV: {str(e)}'}), 500


# ----------------- EXPORT CSV (Async - Send via Email) -----------------
@user_bp.route('/export-csv-async', methods=['POST'])
@jwt_required()
@user_required
def export_csv_async():
    """
    Trigger async CSV export task.
    The CSV will be generated in the background and sent via email.
    """
    try:
        user_id = int(get_jwt_identity())

        if not CELERY_AVAILABLE:
            return jsonify({
                'message': 'Async export not available. Celery is not configured.'
            }), 503

        # Get user info for response
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404

        if not user.email:
            return jsonify({
                'message': 'No email address on file. Please update your profile.'
            }), 400

        # Trigger async task
        task = export_user_csv_task.apply_async(args=[user_id])

        return jsonify({
            'message': f'CSV export started. You will receive an email at {user.email} when ready.',
            'task_id': task.id,
            'email': user.email,
            'status': 'processing'
        }), 202  # 202 Accepted

    except Exception as e:
        print(f"Error in export_csv_async: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'message': f'Error starting export: {str(e)}'}), 500


# ----------------- CHECK CSV EXPORT STATUS -----------------
@user_bp.route('/export-csv-status/<task_id>', methods=['GET'])
@jwt_required()
@user_required
def check_csv_export_status(task_id):
    """Check the status of an async CSV export task"""
    try:
        if not CELERY_AVAILABLE:
            return jsonify({'message': 'Celery not available'}), 503

        from celery.result import AsyncResult
        task = AsyncResult(task_id, app=celery_app)

        if task.state == 'PENDING':
            response = {
                'status': 'pending',
                'message': 'Task is waiting to be processed'
            }
        elif task.state == 'STARTED':
            response = {
                'status': 'processing',
                'message': 'CSV is being generated...'
            }
        elif task.state == 'SUCCESS':
            result = task.result
            response = {
                'status': 'completed',
                'message': result.get('message', 'CSV export completed'),
                'filename': result.get('filename'),
                'total_bookings': result.get('total_bookings', 0)
            }
        elif task.state == 'FAILURE':
            response = {
                'status': 'failed',
                'message': str(task.info)
            }
        else:
            response = {
                'status': task.state.lower(),
                'message': 'Unknown task state'
            }

        return jsonify(response), 200

    except Exception as e:
        print(f"Error checking task status: {str(e)}")
        return jsonify({'message': f'Error checking status: {str(e)}'}), 500

