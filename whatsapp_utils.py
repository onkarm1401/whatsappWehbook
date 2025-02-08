import logging
import requests
import os
from firebase_data import get_filtered_firestore_data

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# WhatsApp API details (for sending messages back)
WHATSAPP_API_URL = "https://graph.facebook.com/v12.0/510167355521515/messages"
ACCESS_TOKEN = "EAAJH2BRzadUBO0obGd4O0zoZAQlaeFzvcoMq3SbGGoVOfWv9RIy33oCYyCf0aZC2XyimQITyFnywKjKrPQ2IP3jKSRcJ4wVFI4ZAUMFiAHb2OsvZAOVEYjLSiBzU5Tlfy4ghN65MZBjFqcCtKV5Lr2pW9RmqEIZACVTpdmiVgup9x161X3DSZAZArci23uJyGZApIBxhGWpz1XyZAdBHTvChZCwDDuSG75ZBkbyIF5sZD"  
# Store your token in environment variable

def extract_and_log_message(sender_id, message,owner_phone_number):
    """Extract sender ID and message, log them separately, and send a response."""
    logger.info(f"owner_phone_number: {owner_phone_number}")
    logger.info(f"Sender ID: {sender_id}")
    logger.info(f"Message: {message}")

    get_filtered_firestore_data(message,owner_phone_number)

    send_whatsapp_message(sender_id, message)

def send_whatsapp_message(recipient_id, message):
    """Send a message to the specified recipient using the WhatsApp API."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "text": {
            "body": message
        }
    }

    response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        logger.info(f"Message sent to {recipient_id} : {message}")
    else:
        logger.error(f"Failed to send message to {recipient_id}: {response.text}")
