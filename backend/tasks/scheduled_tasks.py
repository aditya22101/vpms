from celery.schedules import crontab
from tasks.celery_app import celery_app
from database import User, Reservation, ParkingLot, db
from datetime import datetime, timedelta
import requests
from config import Config

@celery_app.task(name='tasks.send_daily_reminders')
def send_daily_reminders():
    """Send daily reminders to users who haven't visited or booked parking"""
    try:
        # Get users who haven't booked in the last 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        users = User.query.filter_by(role='user').all()
        reminders_sent = 0
        
        for user in users:
            # Check last booking
            last_booking = Reservation.query.filter_by(
                user_id=user.id
            ).order_by(Reservation.parking_timestamp.desc()).first()
            
            should_remind = False
            
            if not last_booking:
                # User never booked
                should_remind = True
            elif last_booking.parking_timestamp < seven_days_ago:
                # Last booking was more than 7 days ago
                should_remind = True
            
            if should_remind:
                # Send reminder via Google Chat Webhook
                if Config.GOOGLE_CHAT_WEBHOOK_URL:
                    message = {
                        "text": f"Hi {user.username}! 👋\n\n"
                               f"Don't forget to book a parking spot if you need one. "
                               f"Visit VPMS to reserve your spot now!"
                    }
                    try:
                        requests.post(Config.GOOGLE_CHAT_WEBHOOK_URL, json=message, timeout=5)
                        reminders_sent += 1
                    except Exception as e:
                        print(f"Failed to send reminder to {user.username}: {str(e)}")
        
        return {
            'status': 'completed',
            'reminders_sent': reminders_sent,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }

@celery_app.task(name='tasks.send_monthly_reports')
def send_monthly_reports():
    """Send monthly activity reports to all users"""
    try:
        # Get last month's date range
        today = datetime.utcnow()
        first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_day_last_month = today.replace(day=1) - timedelta(days=1)
        
        users = User.query.filter_by(role='user').all()
        reports_sent = 0
        
        for user in users:
            # Get last month's bookings
            bookings = Reservation.query.filter(
                Reservation.user_id == user.id,
                Reservation.parking_timestamp >= first_day_last_month,
                Reservation.parking_timestamp <= last_day_last_month
            ).all()
            
            if not bookings:
                continue  # Skip users with no bookings last month
            
            # Calculate statistics
            total_bookings = len(bookings)
            total_spent = sum(b.parking_cost for b in bookings if b.parking_cost)
            
            # Find most used parking lot
            lot_usage = {}
            for booking in bookings:
                spot = ParkingSpot.query.get(booking.spot_id)
                if spot:
                    lot = ParkingLot.query.get(spot.lot_id)
                    if lot:
                        lot_usage[lot.prime_location_name] = lot_usage.get(lot.prime_location_name, 0) + 1
            
            most_used_lot = max(lot_usage.items(), key=lambda x: x[1])[0] if lot_usage else 'N/A'
            
            # Generate HTML report
            html_report = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #0d6efd; }}
                    .stat {{ margin: 10px 0; padding: 10px; background-color: #f8f9fa; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <h1>Monthly Activity Report - {first_day_last_month.strftime('%B %Y')}</h1>
                <p>Hello {user.username},</p>
                <p>Here's your parking activity summary for last month:</p>
                
                <div class="stat">
                    <strong>Total Bookings:</strong> {total_bookings}
                </div>
                <div class="stat">
                    <strong>Total Amount Spent:</strong> ₹{total_spent:.2f}
                </div>
                <div class="stat">
                    <strong>Most Used Parking Lot:</strong> {most_used_lot}
                </div>
                
                <p>Thank you for using VPMS!</p>
            </body>
            </html>
            """
            
            # In a real implementation, send email
            # For now, just log it
            print(f"Monthly report generated for {user.username}")
            reports_sent += 1
        
        return {
            'status': 'completed',
            'reports_sent': reports_sent,
            'month': first_day_last_month.strftime('%B %Y'),
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }

# Configure scheduled tasks
celery_app.conf.beat_schedule = {
    'send-daily-reminders': {
        'task': 'tasks.send_daily_reminders',
        'schedule': crontab(hour=18, minute=0),  # Every day at 6 PM
    },
    'send-monthly-reports': {
        'task': 'tasks.send_monthly_reports',
        'schedule': crontab(day_of_month=1, hour=9, minute=0),  # First day of month at 9 AM
    },
}

