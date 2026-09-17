import os
import logging
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

def send_sms_notification(to_phone: str, case_id: str, case_title: str, priority: int, department: str, is_update: bool = False):
    """
    Sends an SMS notification to a department official using Twilio.
    """
    if not to_phone:
        logger.warning(f"No phone number provided for case {case_id}")
        return

    # Message Content
    if is_update:
        body = f"📎 UPDATE: New evidence added for Case '{case_title}' in {department}. Priority: {priority}/10. Check Dashboard."
    else:
        body = f"🚨 NEW CASE: '{case_title}' assigned to {department}. Priority: {priority}/10. Check Dashboard."

    # Send SMS if Twilio credentials exist
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_PHONE_NUMBER:
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=body,
                from_=TWILIO_PHONE_NUMBER,
                to=to_phone
            )
            logger.info(f"SMS successfully sent to {to_phone}. Message SID: {message.sid}")
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_phone}: {e}")
    else:
        # Mock SMS for development/testing when keys aren't provided
        print(f"\n📱 [MOCK SMS to {to_phone}]: {body}\n")
        logger.info(f"Twilio credentials missing. Mock SMS sent to {to_phone}.")

def send_citizen_sms_notification(to_phone: str, case_id: str, case_title: str, department: str):
    """
    Sends an SMS notification to the citizen updating them on their case.
    """
    if not to_phone:
        logger.warning(f"No phone number provided for citizen on case {case_id}")
        return

    body = f"✅ UPDATE: Your complaint '{case_title}' was successfully assigned to the {department} department. They are on it! (Case ID: {case_id})"

    # Send SMS if Twilio credentials exist
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_PHONE_NUMBER:
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=body,
                from_=TWILIO_PHONE_NUMBER,
                to=to_phone
            )
            logger.info(f"Citizen SMS successfully sent to {to_phone}. Message SID: {message.sid}")
        except Exception as e:
            logger.error(f"Failed to send citizen SMS to {to_phone}: {e}")
    else:
        # Mock SMS for development/testing when keys aren't provided
        print(f"\n📱 [MOCK CITIZEN SMS to {to_phone}]: {body}\n")
        logger.info(f"Twilio credentials missing. Mock citizen SMS sent to {to_phone}.")
