import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

def send_department_notification(to_email: str, case_id: str, case_title: str, priority: int, department: str, ward: str, latitude: float, longitude: float):
    """
    Sends an SMTP email notification to a department official, including location.
    """
    if not settings.SMTP_SERVER or not settings.SENDER_EMAIL or not settings.SENDER_PASSWORD:
        logger.warning(f"SMTP not configured. Skipping email to {to_email}")
        return

    subject = f"🚨 New Case Assigned in {ward}: {case_title} (Priority: {priority})"
    body = f"""
    <html>
        <body>
            <h2>New Case Assigned to {department}</h2>
            <p><strong>Case ID:</strong> {case_id}</p>
            <p><strong>Title:</strong> {case_title}</p>
            <p><strong>Priority Score:</strong> {priority}/10</p>
            <p><strong>Location:</strong> {ward} (Lat: {latitude}, Lng: {longitude}) 📍</p>
            <p>Please log in to the Civic System Dashboard to view full details and take action.</p>
        </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = settings.SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
        server.send_message(msg)
        logger.info(f"Notification email sent successfully to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
    finally:
        try:
            server.quit()
        except:
            pass
