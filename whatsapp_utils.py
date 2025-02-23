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
ACCESS_TOKEN = "EAAJH2BRzadUBOwPv7MTI0648H7IuxMgRpZCxOlW2Eo4IcI9tP4jeaSQ8cK4JpSv7ZAnXShFSwn1DFzppd0W09M8YEPqVUJ7rtfXxBKSeBaEnyKXU33mh4EsF3S2Emp6knAkAlF5fjIIKQg2ZCH6bZB3zb4h02kbA852QiefzqSOLveZCK0IKWrQUi2OfH1mZArT2FOsAaAIDiYXHymracIuj5VSA1LE1yVMRwZD"  
# Store your token in environment variable

def extract_and_log_message(sender_id, message,owner_phone_number):
    """Extract sender ID and message, log them separately, and send a response."""
    logger.info(f"owner_phone_number: {owner_phone_number}")
    logger.info(f"Sender ID: {sender_id}")
    logger.info(f"Message: {message}")

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
            "body": "message"
        }
    }

    response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
    initialize_firebase().collection("whatsapp-execution-logs").add({"api-type": "POST","response": response , "created-at": get_current_ist_time()})

    if response.status_code == 200:
        logger.info(f"Message sent to {recipient_id} : {message}")
        users_ref = db.collection("whatsapp-messages")
        users_ref.add({"owner-number": owner_phone_number,"owner-message":message, "user-number":recipient_id ,"user-message": message ,"created-date": get_current_ist_time})
    else:
        logger.error(f"Failed to send message to {recipient_id}: {response.text}")
