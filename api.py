import logging
import requests
import json
from global_vars import *
from firestore_config import initialize_firebase
from date_utils import *
from store_data import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

API_VERSION = "v22.0"

def get_url():
    return f"https://graph.facebook.com/{API_VERSION}/{get_owner_number()}/messages"

def get_header():
    access_key = get_access_key()
    if not access_key:
        logger.error("Access key is missing.")
        return None
    return {"Content-Type": "application/json", "Authorization": f"Bearer {access_key}"}

def execute_request(api_name, data):
    if get_status() == "COMPLETED":
        logger.warning(f"Skipping {api_name} execution: Already completed.")
        return {"status": "skipped", "message": f"{api_name} execution skipped."}

    url = get_url()
    headers = get_header()

    if not url or not headers:
        logger.error(f"Cannot execute {api_name}: Missing URL or headers.")
        return {"status": "error", "message": "Missing required credentials"}

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        response_data = response.json()

        logger.info(f"{api_name} executed successfully: {response_data}")
        
        mark_message_as_read()
        update_status("COMPLETED")
        return {"status": "success", "response": response_data}
    
    except requests.RequestException as e:
        logger.error(f"Error executing {api_name}: {str(e)}")
        return {"status": "error", "message": str(e)}

def send_whatsapp_message():
    logger.info("Inside send_whatsapp_message") 
    data = {
        "messaging_product": "whatsapp",
        "to": get_user_number(),
        "text": {"body": get_owner_reply_message()}
    }
    return execute_request("send_whatsapp_message", data)

def mark_message_as_read():
    message_id = get_message_id()
    if not message_id:
        logger.warning("Skipping mark_message_as_read: No message ID available.")
        return {"status": "skipped", "message": "No message ID found."}

    logger.info(f"Marking message {message_id} as read")
    data = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id
    }
    
    url = get_url()
    headers = get_header()

    if url and headers:
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            logger.info(f"Message {message_id} marked as read successfully.")
        except requests.RequestException as e:
            logger.error(f"Error marking message as read: {str(e)}")

def send_image_message():
    logger.info(f"Sending image message to {get_owner_reply_message()}")
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": get_user_number(),
        "type": "image",
        "image": {"link": get_image_path()}
    }
    return execute_request("send_image_message", data)

def send_youtube_video():
    logger.info(f"Sending YouTube video to {get_owner_reply_message()}")

    data = {
        "messaging_product": "whatsapp",
        "to": get_user_number(),
        "text": {
            "preview_url": True,
            "body": get_owner_reply_message()
        }
    }
    return execute_request("send_youtube_video", data)

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

def send_button_menu():
    logger.info(f"Sending reply button message to {get_user_number()}")
    
    buttons_data = get_button_menu_options()
    if isinstance(buttons_data, str):
        try:
            buttons_data = json.loads(buttons_data)
        except json.JSONDecodeError:
            logger.error("Error decoding button menu options JSON")
            return {"status": "error", "message": "Invalid button menu format"}

    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": get_user_number(),
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": get_owner_reply_message()},
            "action": {"buttons": buttons_data}
        }
    }
    
    logger.info(f"Button menu data: {data}")
    return execute_request("send_reply_button", data)
