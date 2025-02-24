import logging
import requests
import os
import json
from date_utils import get_current_ist_time
from firestore_config import initialize_firebase
from global_vars import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

API_VERSION = "v12.0"

def get_url():
    try:
        return f"https://graph.facebook.com/{API_VERSION}/{get_owner_number()}/messages"
    except Exception as e:
        logger.error(f"Error generating API URL: {e}")
        return None

def get_header():
    try:
        return {"Content-Type": "application/json", "Authorization": f"Bearer {get_access_key()}"}
    except Exception as e:
        logger.error(f"Error generating headers: {e}")
        return None

def send_whatsapp_message():
    try:
        logger.info(f"Sending WhatsApp message to {get_user_number()}")

        data = {
            "messaging_product": "whatsapp",
            "to": get_user_number(),
            "text": {"body": get_owner_reply_message()}
        }

        return execute_request(data)
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}")
        return {"success": False, "error": str(e)}

def mark_message_as_read():
    try:
        logger.info(f"Marking message {get_message_id()} as read")

        data = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": get_message_id()
        }

        return execute_request(data)
    except Exception as e:
        logger.error(f"Error marking message as read: {e}")
        return {"success": False, "error": str(e)}

def send_text_message():
    try:
        logger.info(f"Sending text message to {get_user_number()}")

        data = {
            "messaging_product": "whatsapp",
            "to": get_user_number(),
            "type": "text",
            "text": {"preview_url": False, "body": get_owner_reply_message()}
        }

        return execute_request(data)
    except Exception as e:
        logger.error(f"Error sending text message: {e}")
        return {"success": False, "error": str(e)}

def send_reply_to_message():
    try:
        logger.info(f"Replying to message {get_message_id()} for {get_user_number()}")

        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": get_user_number(),
            "context": {"message_id": get_message_id()},
            "type": "text",
            "text": {"preview_url": False, "body": get_owner_reply_message()}
        }

        return execute_request(data)
    except Exception as e:
        logger.error(f"Error sending reply message: {e}")
        return {"success": False, "error": str(e)}

def send_image_message():
    try:
        logger.info(f"Sending image message to {get_user_number()}")

        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": get_user_number(),
            "type": "image",
            "image": {"link": get_user_message()}
        }

        return execute_request(data)
    except Exception as e:
        logger.error(f"Error sending image message: {e}")
        return {"success": False, "error": str(e)}

def send_list_message():
    try:
        logger.info(f"Sending list message to {get_user_number()}")

        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": get_user_number(),
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": "Select an option"},
                "body": {"text": "Choose one of the options below"},
                "footer": {"text": "Powered by Botto"},
                "action": {"button": "Select", "sections": []}
            }
        }

        return execute_request(data)
    except Exception as e:
        logger.error(f"Error sending list message: {e}")
        return {"success": False, "error": str(e)}

def send_reply_button():
    try:
        logger.info(f"Sending reply button message to {get_user_number()}")

        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": get_user_number(),
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": "Please choose an option"},
                "action": {"buttons": [{"type": "reply", "reply": {"id": "1", "title": "Option 1"}}]}
            }
        }

        return execute_request(data)
    except Exception as e:
        logger.error(f"Error sending reply button message: {e}")
        return {"success": False, "error": str(e)}

def execute_request(data):
    try:
        url = get_url()
        headers = get_header()
        
        if not url or not headers:
            raise ValueError("Invalid API URL or headers")

        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send message: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"success": False, "error": str(e)}
