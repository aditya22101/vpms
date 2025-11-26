from tasks.celery_app import celery_app
from database import Reservation, ParkingSpot, ParkingLot, User, db
import csv
import io
from datetime import datetime

@celery_app.task(name='tasks.export_user_csv')
def export_user_csv_task(user_id):
    """Export user booking history as CSV"""
    try:
        reservations = Reservation.query.filter_by(user_id=user_id).order_by(
            Reservation.parking_timestamp.desc()
        ).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Reservation ID',
            'Spot ID',
            'Parking Lot',
            'Parking Timestamp',
            'Leaving Timestamp',
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
                res.parking_timestamp.isoformat() if res.parking_timestamp else '',
                res.leaving_timestamp.isoformat() if res.leaving_timestamp else '',
                res.parking_cost,
                'Active' if not res.leaving_timestamp else 'Completed',
                res.remarks or ''
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        # In a real implementation, you would:
        # 1. Save CSV to a file or cloud storage
        # 2. Send email with download link
        # 3. Or return the CSV content
        
        return {
            'status': 'completed',
            'csv_content': csv_content,
            'filename': f'parking-history-{user_id}-{datetime.now().strftime("%Y%m%d")}.csv'
        }
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }


