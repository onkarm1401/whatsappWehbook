import logging
import requests
import json
from global_vars import *
from firestore_config import initialize_firebase
from date_utils import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

API_VERSION = "v22.0"

def get_url():
    return f"https://graph.facebook.com/{API_VERSION}/{get_owner_number()}/messages"

def get_header():
    return {"Content-Type": "application/json", "Authorization": f"Bearer {get_access_key()}"}

def send_whatsapp_message():
    logger.info("Inside send_whatsapp_message") 
    data = {
        "messaging_product": "whatsapp",
        "to": get_user_number(),
        "text": {"body": get_owner_reply_message()}
    }
    response = execute_request("send_whatsapp_message", data)

def execute_request(api_name, data):

    response = requests.post(get_url(), json=data, headers=get_header())
    response_data = response.json()
    update_status()  

    logger.info(f"{api_name} executed successfully: {response_data}")

def mark_message_as_read():
    logger.info(f"Marking message {get_message_id()} as read")
    data = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": get_message_id()}
    response = execute_request("mark_message_as_read", data)

def send_image_message():
    logger.info(f"Sending image message to {get_owner_reply_message()}")
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": get_user_number(),
        "type": "image",
        "image": {"link": get_owner_reply_message}
    }
    return execute_request("send_image_message", data)