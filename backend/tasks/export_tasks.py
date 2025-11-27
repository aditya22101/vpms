from tasks.celery_app import celery_app
from database import Reservation, ParkingSpot, ParkingLot, User, db
from config import Config
import csv
import io
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

@celery_app.task(name='tasks.export_user_csv')
def export_user_csv_task(user_id):
    """
    Asynchronous task to export user booking history as CSV and send via email.

    This function:
    1. Retrieves all booking history for the user
    2. Generates a detailed CSV file with all parking information
    3. Sends the CSV file via email to the user
    4. Returns the result status
    """
    try:
        # Get user information
        user = User.query.get(user_id)
        if not user:
            return {
                'status': 'failed',
                'error': 'User not found'
            }

        # Get all reservations for the user
        reservations = Reservation.query.filter_by(user_id=user_id).order_by(
            Reservation.parking_timestamp.desc()
        ).all()

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header with comprehensive information
        writer.writerow([
            'Reservation ID',
            'Spot ID',
            'Parking Lot Name',
            'Parking Lot Address',
            'PIN Code',
            'Parking In Timestamp',
            'Parking Out Timestamp',
            'Duration (Hours)',
            'Price per Hour (₹)',
            'Total Cost (₹)',
            'Status',
            'Remarks'
        ])

        # Calculate totals for summary
        total_bookings = len(reservations)
        total_cost = 0
        total_hours = 0

        # Write data rows
        for res in reservations:
            spot = ParkingSpot.query.get(res.spot_id)
            lot = ParkingLot.query.get(spot.lot_id) if spot else None

            # Calculate duration
            duration = 0
            if res.leaving_timestamp and res.parking_timestamp:
                duration = (res.leaving_timestamp - res.parking_timestamp).total_seconds() / 3600
                total_hours += duration

            total_cost += res.parking_cost if res.parking_cost else 0

            writer.writerow([
                res.id,
                res.spot_id,
                lot.prime_location_name if lot else 'Unknown',
                lot.address if lot else 'N/A',
                lot.pin_code if lot else 'N/A',
                res.parking_timestamp.strftime('%Y-%m-%d %H:%M:%S') if res.parking_timestamp else '',
                res.leaving_timestamp.strftime('%Y-%m-%d %H:%M:%S') if res.leaving_timestamp else 'Active',
                f'{duration:.2f}' if duration else '0.00',
                lot.price if lot else 'N/A',
                f'{res.parking_cost:.2f}' if res.parking_cost else '0.00',
                'Active' if not res.leaving_timestamp else 'Completed',
                res.remarks or ''
            ])

        # Add summary section
        writer.writerow([])  # Empty row
        writer.writerow(['SUMMARY'])
        writer.writerow(['Total Bookings', total_bookings])
        writer.writerow(['Total Hours Parked', f'{total_hours:.2f}'])
        writer.writerow(['Total Amount Spent', f'₹{total_cost:.2f}'])
        writer.writerow(['Average Cost per Booking', f'₹{total_cost/total_bookings:.2f}' if total_bookings > 0 else '₹0.00'])
        writer.writerow(['Export Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])

        csv_content = output.getvalue()
        output.close()

        filename = f'vpms-parking-history-{user.username}-{datetime.now().strftime("%Y%m%d-%H%M%S")}.csv'

        # Send email with CSV attachment
        if user.email and Config.MAIL_USERNAME and Config.MAIL_PASSWORD:
            try:
                # Create email
                msg = MIMEMultipart()
                msg['Subject'] = f'VPMS - Your Parking History Export'
                msg['From'] = Config.MAIL_USERNAME
                msg['To'] = user.email

                # Email body
                body = f"""
                <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
                        }}
                        .container {{
                            max-width: 600px;
                            margin: 0 auto;
                            padding: 20px;
                        }}
                        .header {{
                            background-color: #667eea;
                            color: white;
                            padding: 20px;
                            text-align: center;
                            border-radius: 5px;
                        }}
                        .content {{
                            padding: 20px;
                            background-color: #f9f9f9;
                            margin-top: 20px;
                            border-radius: 5px;
                        }}
                        .stats {{
                            background-color: white;
                            padding: 15px;
                            margin: 10px 0;
                            border-left: 4px solid #667eea;
                        }}
                        .footer {{
                            text-align: center;
                            margin-top: 20px;
                            font-size: 12px;
                            color: #666;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>🅿️ VPMS - Parking History Export</h2>
                        </div>
                        <div class="content">
                            <p>Hello <strong>{user.username}</strong>,</p>
                            <p>Your parking history export is ready! Please find the CSV file attached to this email.</p>

                            <div class="stats">
                                <h3>Export Summary:</h3>
                                <ul>
                                    <li><strong>Total Bookings:</strong> {total_bookings}</li>
                                    <li><strong>Total Hours:</strong> {total_hours:.2f} hours</li>
                                    <li><strong>Total Spent:</strong> ₹{total_cost:.2f}</li>
                                    <li><strong>Export Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                                </ul>
                            </div>

                            <p>The attached CSV file contains:</p>
                            <ul>
                                <li>Complete booking history with timestamps</li>
                                <li>Parking lot details and addresses</li>
                                <li>Duration and cost information</li>
                                <li>Summary statistics</li>
                            </ul>

                            <p>You can open this file in Excel, Google Sheets, or any spreadsheet application.</p>
                        </div>
                        <div class="footer">
                            <p>© {datetime.now().year} Vehicle Parking Management System</p>
                            <p>This is an automated email. Please do not reply.</p>
                        </div>
                    </div>
                </body>
                </html>
                """

                msg.attach(MIMEText(body, 'html'))

                # Attach CSV file
                attachment = MIMEBase('text', 'csv')
                attachment.set_payload(csv_content.encode('utf-8'))
                encoders.encode_base64(attachment)
                attachment.add_header('Content-Disposition', f'attachment; filename={filename}')
                msg.attach(attachment)

                # Send email
                with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
                    server.starttls()
                    server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
                    server.send_message(msg)

                print(f"✅ CSV export sent to {user.username} ({user.email})")

                return {
                    'status': 'completed',
                    'message': f'CSV exported and sent to {user.email}',
                    'filename': filename,
                    'total_bookings': total_bookings,
                    'total_cost': total_cost,
                    'csv_content': csv_content  # Include for immediate download if needed
                }

            except Exception as e:
                print(f"❌ Failed to send CSV to {user.email}: {str(e)}")
                # Still return the CSV content even if email fails
                return {
                    'status': 'completed_no_email',
                    'message': f'CSV generated but email failed: {str(e)}',
                    'filename': filename,
                    'csv_content': csv_content
                }
        else:
            # No email configured, just return CSV content
            return {
                'status': 'completed_no_email',
                'message': 'CSV generated but no email configuration',
                'filename': filename,
                'csv_content': csv_content
            }

    except Exception as e:
        print(f"❌ Error in export_user_csv_task: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'status': 'failed',
            'error': str(e)
        }


