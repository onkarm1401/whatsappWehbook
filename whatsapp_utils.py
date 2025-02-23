import logging
import requests
import os
from date_utils import get_current_ist_time
from firestore_config import initialize_firebase

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# WhatsApp API details (for sending messages back)
WHATSAPP_API_URL = "https://graph.facebook.com/v12.0/510167355521515/messages"
ACCESS_TOKEN = "EAAJH2BRzadUBO7Cpf0cZATVcFSW1gOt2GvYPTSnxMDI7ufj9sOxsDlAdErmJcAZCTkbDRwZCDi1QsBkxvT1g6O6GqYW6QviJGwg3P9VjY81Ex33qxtZAEVVayuomNMI9mBZBJHLVv9yBgWkUmxQXQckBUo0EWbBbySYegLZB6RhcLFHRrUmP00hRGA63KAwI9ITyHzWUwW7PKZB5J5eWY3TQefQDrASAy3vgDQZD"  


def send_whatsapp_message(user_number, message,owner_phone_number):
    """Send a message to the specified recipient using the WhatsApp API."""
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

    response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
    text_response = response.text
    initialize_firebase().collection("whatsapp-execution-logs").add({"api-type": "POST","response": text_response , "created-at": get_current_ist_time()})

    if response.status_code == 200:
        logger.info(f"Message sent to {user_number} : {message}")
        users_ref = initialize_firebase().collection("whatsapp-messages")
        users_ref.add({"owner-number": owner_phone_number,"owner-message":message, "user-number":user_number ,"user-message": message ,"created-date": get_current_ist_time})
    else:
        logger.error(f"Failed to send message to {user_number}: {response.text}")
