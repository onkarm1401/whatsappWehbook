import logging
import requests
import os
from date_utils import get_current_ist_time
from firestore_config import initialize_firebase
import json

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def send_whatsapp_message(user_number, reply_message, owner_phone_number, key_value):
    logger.info(f"Sending WhatsApp message: User: {user_number}, Reply: {reply_message}, Owner: {owner_phone_number}, Key: {key_value}")

    WHATSAPP_API_URL = f"https://graph.facebook.com/v12.0/{owner_phone_number}/messages"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key_value}",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": user_number,
        "text": {
            "body": reply_message
        }
    }

    return requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
