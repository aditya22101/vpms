from celery.schedules import crontab
from tasks.celery_app import celery_app
from database import User, Reservation, ParkingLot, ParkingSpot, db
from datetime import datetime, timedelta
import requests
from config import Config
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_reminder(user_email, username, available_lots_count, new_lots_today):
    """Send email reminder to user"""
    try:
        if not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
            return False

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'VPMS - Parking Reminder'
        msg['From'] = Config.MAIL_USERNAME
        msg['To'] = user_email

        # Create HTML content
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0d6efd; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f8f9fa; }}
                .button {{ background-color: #0d6efd; color: white; padding: 10px 20px; text-decoration: none; display: inline-block; margin: 10px 0; }}
                .highlight {{ background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🅿️ VPMS - Vehicle Parking Management System</h2>
                </div>
                <div class="content">
                    <h3>Hi {username}! 👋</h3>
                    <p>This is your daily parking reminder.</p>

                    {"<div class='highlight'><strong>🎉 New Parking Lots Available!</strong><br>" + str(new_lots_today) + " new parking lot(s) were added today.</div>" if new_lots_today > 0 else ""}

                    <p><strong>Currently available: {available_lots_count} parking lot(s)</strong></p>

                    <p>Don't forget to book a parking spot if you need one for today or tomorrow!</p>

                    <p style="text-align: center;">
                        <a href="#" class="button">Book Parking Now</a>
                    </p>

                    <p style="font-size: 12px; color: #666;">
                        You're receiving this because you're registered with VPMS.
                        This reminder is sent daily to help you secure parking.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        part = MIMEText(html, 'html')
        msg.attach(part)

        # Send email
        with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
            server.starttls()
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        print(f"Failed to send email to {user_email}: {str(e)}")
        return False

@celery_app.task(name='tasks.send_daily_reminders')
def send_daily_reminders():
    """Send daily reminders to users who haven't visited or booked parking"""
    try:
        # Get users who haven't booked in the last 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        # Check if any new parking lots were created today
        new_lots_today = ParkingLot.query.filter(
            ParkingLot.created_at >= today_start
        ).count()

        # Get available parking lots count
        available_lots = []
        all_lots = ParkingLot.query.all()
        for lot in all_lots:
            available_count = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count()
            if available_count > 0:
                available_lots.append({
                    'name': lot.prime_location_name,
                    'available': available_count
                })

        users = User.query.filter_by(role='user').all()
        reminders_sent = 0
        email_sent = 0
        chat_sent = 0

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

            # Also remind if new parking lots were created today
            if new_lots_today > 0:
                should_remind = True

            if should_remind:
                # Send reminder via Email
                if user.email and send_email_reminder(
                    user.email,
                    user.username,
                    len(available_lots),
                    new_lots_today
                ):
                    email_sent += 1

                # Send reminder via Google Chat Webhook
                if Config.GOOGLE_CHAT_WEBHOOK_URL:
                    lots_info = '\n'.join([f"  • {lot['name']}: {lot['available']} spots" for lot in available_lots[:3]])
                    new_lot_msg = f"\n🎉 *{new_lots_today} new parking lot(s) added today!*\n" if new_lots_today > 0 else ""

                    message = {
                        "text": f"Hi {user.username}! 👋\n\n"
                               f"*Daily Parking Reminder*\n"
                               f"{new_lot_msg}\n"
                               f"Currently available: *{len(available_lots)} parking lot(s)*\n\n"
                               f"Top Locations:\n{lots_info}\n\n"
                               f"Don't forget to book a parking spot if you need one!\n"
                               f"Visit VPMS to reserve your spot now! 🚗"
                    }
                    try:
                        requests.post(Config.GOOGLE_CHAT_WEBHOOK_URL, json=message, timeout=5)
                        chat_sent += 1
                    except Exception as e:
                        print(f"Failed to send chat reminder to {user.username}: {str(e)}")

                reminders_sent += 1

        return {
            'status': 'completed',
            'reminders_sent': reminders_sent,
            'email_sent': email_sent,
            'chat_sent': chat_sent,
            'new_lots_today': new_lots_today,
            'available_lots': len(available_lots),
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        print(f"Error in send_daily_reminders: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'status': 'failed',
            'error': str(e)
        }

@celery_app.task(name='tasks.send_monthly_reports')
def send_monthly_reports():
    """Send monthly activity reports to all users via email"""
    try:
        # Get last month's date range
        today = datetime.utcnow()
        first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_day_last_month = today.replace(day=1) - timedelta(days=1)

        users = User.query.filter_by(role='user').all()
        reports_sent = 0
        email_sent = 0

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

            # Calculate total parking duration (hours)
            total_hours = 0
            for booking in bookings:
                if booking.leaving_timestamp and booking.parking_timestamp:
                    duration = (booking.leaving_timestamp - booking.parking_timestamp).total_seconds() / 3600
                    total_hours += duration

            # Find most used parking lot and its usage count
            lot_usage = {}
            for booking in bookings:
                spot = ParkingSpot.query.get(booking.spot_id)
                if spot:
                    lot = ParkingLot.query.get(spot.lot_id)
                    if lot:
                        lot_name = lot.prime_location_name
                        lot_usage[lot_name] = lot_usage.get(lot_name, 0) + 1

            most_used_lot = max(lot_usage.items(), key=lambda x: x[1])[0] if lot_usage else 'N/A'
            most_used_count = lot_usage.get(most_used_lot, 0) if most_used_lot != 'N/A' else 0

            # Calculate average cost per booking
            avg_cost = total_spent / total_bookings if total_bookings > 0 else 0

            # Get breakdown by parking lot
            lot_breakdown = []
            for lot_name, count in sorted(lot_usage.items(), key=lambda x: x[1], reverse=True):
                lot_breakdown.append(f"<li><strong>{lot_name}:</strong> {count} visit(s)</li>")
            lot_breakdown_html = '\n'.join(lot_breakdown) if lot_breakdown else '<li>No data available</li>'

            # Generate enhanced HTML report
            html_report = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        margin: 0;
                        padding: 0;
                        background-color: #f4f4f4;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 20px auto;
                        background-color: white;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        overflow: hidden;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 28px;
                    }}
                    .header p {{
                        margin: 10px 0 0 0;
                        opacity: 0.9;
                    }}
                    .content {{
                        padding: 30px;
                    }}
                    .greeting {{
                        font-size: 18px;
                        color: #333;
                        margin-bottom: 20px;
                    }}
                    .stats-grid {{
                        display: table;
                        width: 100%;
                        margin: 20px 0;
                    }}
                    .stat-row {{
                        display: table-row;
                    }}
                    .stat-cell {{
                        display: table-cell;
                        padding: 15px;
                        margin: 10px 0;
                        background-color: #f8f9fa;
                        border-radius: 8px;
                        text-align: center;
                        width: 50%;
                    }}
                    .stat-cell:first-child {{
                        margin-right: 10px;
                    }}
                    .stat-value {{
                        font-size: 32px;
                        font-weight: bold;
                        color: #667eea;
                        display: block;
                    }}
                    .stat-label {{
                        font-size: 14px;
                        color: #666;
                        margin-top: 5px;
                        display: block;
                    }}
                    .section {{
                        margin: 25px 0;
                        padding: 20px;
                        background-color: #f8f9fa;
                        border-radius: 8px;
                        border-left: 4px solid #667eea;
                    }}
                    .section h3 {{
                        margin-top: 0;
                        color: #333;
                        font-size: 18px;
                    }}
                    .section ul {{
                        margin: 10px 0;
                        padding-left: 20px;
                    }}
                    .section li {{
                        margin: 8px 0;
                        color: #555;
                    }}
                    .highlight {{
                        background-color: #fff3cd;
                        padding: 15px;
                        border-radius: 8px;
                        border-left: 4px solid #ffc107;
                        margin: 20px 0;
                    }}
                    .footer {{
                        background-color: #f8f9fa;
                        padding: 20px;
                        text-align: center;
                        font-size: 12px;
                        color: #666;
                    }}
                    .footer a {{
                        color: #667eea;
                        text-decoration: none;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🅿️ Monthly Activity Report</h1>
                        <p>{first_day_last_month.strftime('%B %Y')}</p>
                    </div>

                    <div class="content">
                        <div class="greeting">
                            Hello <strong>{user.username}</strong>,
                        </div>
                        <p>Here's your parking activity summary for last month. Thank you for using VPMS!</p>

                        <table class="stats-grid" cellpadding="5">
                            <tr class="stat-row">
                                <td class="stat-cell">
                                    <span class="stat-value">{total_bookings}</span>
                                    <span class="stat-label">Total Bookings</span>
                                </td>
                                <td class="stat-cell">
                                    <span class="stat-value">₹{total_spent:.2f}</span>
                                    <span class="stat-label">Total Spent</span>
                                </td>
                            </tr>
                            <tr><td colspan="2" style="height: 10px;"></td></tr>
                            <tr class="stat-row">
                                <td class="stat-cell">
                                    <span class="stat-value">{total_hours:.1f}</span>
                                    <span class="stat-label">Hours Parked</span>
                                </td>
                                <td class="stat-cell">
                                    <span class="stat-value">₹{avg_cost:.2f}</span>
                                    <span class="stat-label">Avg Cost/Booking</span>
                                </td>
                            </tr>
                        </table>

                        <div class="highlight">
                            <strong>🏆 Most Used Parking Lot:</strong><br>
                            {most_used_lot} ({most_used_count} visit{'s' if most_used_count != 1 else ''})
                        </div>

                        <div class="section">
                            <h3>📍 Parking Lot Breakdown</h3>
                            <ul>
                                {lot_breakdown_html}
                            </ul>
                        </div>

                        <p style="text-align: center; margin-top: 30px;">
                            <a href="#" style="background-color: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                View Full History
                            </a>
                        </p>
                    </div>

                    <div class="footer">
                        <p>This is an automated monthly report from VPMS.</p>
                        <p>© {datetime.utcnow().year} Vehicle Parking Management System</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Send email
            if user.email and Config.MAIL_USERNAME and Config.MAIL_PASSWORD:
                try:
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = f'VPMS Monthly Report - {first_day_last_month.strftime("%B %Y")}'
                    msg['From'] = Config.MAIL_USERNAME
                    msg['To'] = user.email

                    part = MIMEText(html_report, 'html')
                    msg.attach(part)

                    with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
                        server.starttls()
                        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
                        server.send_message(msg)

                    email_sent += 1
                    print(f"✅ Monthly report sent to {user.username} ({user.email})")
                except Exception as e:
                    print(f"❌ Failed to send report to {user.username}: {str(e)}")
            else:
                print(f"⚠️ Skipping {user.username} - No email or mail config missing")

            reports_sent += 1

        return {
            'status': 'completed',
            'reports_sent': reports_sent,
            'email_sent': email_sent,
            'month': first_day_last_month.strftime('%B %Y'),
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        print(f"❌ Error in send_monthly_reports: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'status': 'failed',
            'error': str(e)
        }

# Configure scheduled tasks
# Students can configure the reminder time in .env file
celery_app.conf.beat_schedule = {
    'send-daily-reminders': {
        'task': 'tasks.send_daily_reminders',
        'schedule': crontab(
            hour=Config.REMINDER_HOUR,
            minute=Config.REMINDER_MINUTE
        ),  # Configurable time (default: 6 PM)
    },
    'send-monthly-reports': {
        'task': 'tasks.send_monthly_reports',
        'schedule': crontab(day_of_month=1, hour=9, minute=0),  # First day of month at 9 AM
    },
}

