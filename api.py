import logging
import requests
import os
from date_utils import get_current_ist_time
from firestore_config import initialize_firebase
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_url(owner_phone_number):
    return f"https://graph.facebook.com/v12.0/{owner_phone_number}/messages"

def get_header(key_value):
    return {"Content-Type": "application/json", "Authorization": f"Bearer {key_value}"}

def send_whatsapp_message(user_number, reply_message, owner_phone_number, key_value):
    logger.info(f"Sending WhatsApp message: User: {user_number}, Reply: {reply_message}, Owner: {owner_phone_number}")

    payload = {
        "messaging_product": "whatsapp",
        "to": user_number,
        "text": {"body": reply_message}
    }

    try:
        response = requests.post(get_url(owner_phone_number), json=payload, headers=get_header(key_value))
        response.raise_for_status()  # Raise an error for non-200 responses

        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = {"error": "Invalid JSON response from WhatsApp API"}

        logger.info(f"Message sent successfully: {response_data}")
        return {"success": True, "response": response_data}  # Return structured response

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send message to {user_number}: {e}")
        return {"success": False, "error": str(e)}  # Return failure response
