import logging
import requests
import os
from date_utils import get_current_ist_time
from firestore_config import initialize_firebase
import json
from personal_information import get_linked_phone_number , get_key_value

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

WHATSAPP_API_URL = f"https://graph.facebook.com/v12.0/{get_linked_phone_number}/messages"

def send_whatsapp_message(user_number, message,owner_phone_number,key_value):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key_value}",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": user_number,
        "text": {
            "body": "message"
        }
    }

    return requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
