import logging
import requests
import os
from date_utils import get_current_ist_time
from firestore_config import initialize_firebase
import json

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# WhatsApp API details (for sending messages back)
WHATSAPP_API_URL = "https://graph.facebook.com/v12.0/510167355521515/messages"
ACCESS_TOKEN = "EAAJH2BRzadUBO4W1ZB8SKBZC8w2cW4VlJYVOKLBnvngZAdFeRdflAYZC1tqfwEgZAFomqvCHsJ4SkKxz6UVH09Igadyj3gmgONKQxx9rQytFAZB33xXpPW6oUUvwZBLbFHDW2qd9Fh84xsmB3lagrkZCH0C1zn7ChtP68FeV4QvxARg8qdTA7yhZBA9Bjr88q14XSZAky3FtiRUCmUw1otidfSTjgvSKEhZBZArywZAMZD"  


def send_whatsapp_message(user_number, message,owner_phone_number):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": user_number,
        "text": {
            "body": "message"
        }
    }

    return requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
