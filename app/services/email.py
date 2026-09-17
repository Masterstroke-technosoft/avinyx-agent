import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

def send_department_notification(to_email: str, case_id: str, case_title: str, priority: int, department: str, ward: str, latitude: float, longitude: float, attachment_path: str = None, is_update: bool = False):
    """
    Sends an SMTP email notification to a department official, including location and optional attachment.
    """
    if not settings.SMTP_SERVER or not settings.SENDER_EMAIL or not settings.SENDER_PASSWORD:
        logger.warning(f"SMTP not configured. Skipping email to {to_email}")
        return

    if is_update:
        subject = f"📎 UPDATE: New Evidence Added for Case: {case_title} (Priority: {priority})"
        title_html = f"<h2>New Evidence Uploaded for Case in {department}</h2>"
    else:
        subject = f"🚨 New Case Assigned in {ward}: {case_title} (Priority: {priority})"
        title_html = f"<h2>New Case Assigned to {department}</h2>"

    body = f"""
    <html>
        <body>
            {title_html}
            <p><strong>Case ID:</strong> {case_id}</p>
            <p><strong>Title:</strong> {case_title}</p>
            <p><strong>Ward:</strong> {ward}</p>
            <p><strong>Location:</strong> {latitude}, {longitude}</p>
            <p><strong>Priority Score:</strong> {priority}/10</p>
            <p>Please log in to the dashboard to view full details and take action.</p>
        </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = settings.SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))
    
    # Process attachment if it exists
    if attachment_path and os.path.exists(attachment_path):
        try:
            with open(attachment_path, "rb") as attachment_file:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment_file.read())
            encoders.encode_base64(part)
            filename = os.path.basename(attachment_path)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
            msg.attach(part)
        except Exception as e:
            logger.error(f"Failed to attach file {attachment_path}: {e}")

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
