import logging
import requests
import os

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# WhatsApp API details (for sending messages back)
WHATSAPP_API_URL = "https://graph.facebook.com/v12.0/510167355521515/messages"
ACCESS_TOKEN = "EAAJH2BRzadUBOZBxJ4zQShXFofnlBo7LaJpcK0u6U4RBg903ouq2Fbsh3DZCmWe4qZAaYs3VAZCVl1Qb2EVkmnxtjdkPZAH41kEQU2dTlsO0RG1a0aAX6L4FajuGgGMHVPhAeAHk5rMkFdrcdEl9xsyA4de545sZB0DZAF9XHWQWzNeeIY0UvvmvPUfQ7bHEjsXCC6TZBHlFWyuPHsUqvsirAvXbXlaEZBL2ZBV5EZD"  
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
            "body": message
        }
    }

    response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        logger.info(f"Message sent to {recipient_id} : {message}")
    else:
        logger.error(f"Failed to send message to {recipient_id}: {response.text}")
