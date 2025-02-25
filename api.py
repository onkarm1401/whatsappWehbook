import logging
import requests
import json
from global_vars import *
from firestore_config import initialize_firebase

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

API_VERSION = "v12.0"

def get_url():
    return f"https://graph.facebook.com/{API_VERSION}/{get_owner_number()}/messages"

def get_header():
    return {"Content-Type": "application/json", "Authorization": f"Bearer {get_access_key()}"}

def send_whatsapp_message():
    logger.info(f"Sending WhatsApp message to {get_user_number()}")

    data = {
        "messaging_product": "whatsapp",
        "to": get_user_number(),
        "text": {"body": get_owner_reply_message()}
    }

    return execute_request("send_whatsapp_message", data)

def mark_message_as_read():
    logger.info(f"Marking message {get_message_id()} as read")

    data = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": get_message_id()
    }

    return execute_request("mark_message_as_read", data)

def send_text_message():
    logger.info(f"Sending text message to {get_user_number()}")

    data = {
        "messaging_product": "whatsapp",
        "to": get_user_number(),
        "type": "text",
        "text": {"preview_url": True, "body": get_user_message()}
    }

    return execute_request("send_text_message", data)

def send_reply_to_message():
    logger.info(f"Replying to message {get_message_id()} for {get_user_number()}")

    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": get_user_number(),
        "context": {"message_id": get_message_id()},
        "type": "text",
        "text": {"preview_url": False, "body": get_user_message()}
    }

    return execute_request("send_reply_to_message", data)

def send_image_message(image_url):
    logger.info(f"Sending image message to {get_user_number()}")

    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": get_user_number(),
        "type": "image",
        "image": {"link": image_url}
    }

    return execute_request("send_image_message", data)

def send_list_message(header, body, footer, button_text, sections):
    logger.info(f"Sending list message to {get_user_number()}")

    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": get_user_number(),
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": header},
            "body": {"text": body},
            "footer": {"text": footer},
            "action": {"button": button_text, "sections": sections}
        }
    }

    return execute_request("send_list_message", data)

def send_reply_button(button_text, buttons):
    logger.info(f"Sending reply button message to {get_user_number()}")

    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": get_user_number(),
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": button_text},
            "action": {"buttons": buttons}
        }
    }

    return execute_request("send_reply_button", data)

def execute_request(api_name, data):
    if get_status() != "COMPLETED":
        response = requests.post(get_url(), json=data, headers=get_header())
        response_data = response.json()
        
        update_status()  
        logger.info(f"{api_name} executed successfully: {response_data}")
            
    logger.info(f"{api_name} execution skipped as status is already COMPLETED.")
    return None