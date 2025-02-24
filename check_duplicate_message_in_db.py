from firestore_config import initialize_firebase
from date_utils import get_current_ist_time
from api import *
from global_vars import *
from api import *

import logging
logger = logging.getLogger(__name__)

def process_request():
    try:
        db = initialize_firebase()
        results = extract_response(db)  
        get_owner_information(db)
        get_reply_message(db)
        send_whatsapp_message()
              
    except Exception as e:
        logger.error(f"Error processing request: {e}")

def extract_response(db):
    try:
        data = get_data()
        if data and "entry" in data:
            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    if "messages" in change.get("value", {}):
                        message = change["value"]["messages"][0]

                        update_user_number(message["from"])
                        update_message_id(message["id"])
                        update_user_message(message.get("text", {}).get("body", "No text message received"))
                        update_owner_number(change["value"]["metadata"]["phone_number_id"])

                        logger.info(f"Updated user number: {get_user_number()}")
                        logger.info(f"Updated message ID: {get_message_id()}")
                        logger.info(f"Updated user message: {get_user_message()}")
                        logger.info(f"Updated owner number: {get_owner_number()}")

    except Exception as e:
        logger.error(f"Error extracting response: {e}")
        return None  # Return None if an error occurs

def get_owner_information(db):
    try:
        query = db.collection('whatsapp-personal-information') \
            .where('phone_number', '==', get_owner_number()) \
            .stream()

        data_list = [doc.to_dict() for doc in query]
        if data_list:
            owner_info = data_list[0]
            update_owner_number(owner_info.get("phone_number", None))
            update_access_key(owner_info.get("key", None))

    except Exception as e:
        logger.error(f"Error fetching owner information: {e}")

def get_reply_message(db):
    try:
        reply_message_collection = db.collection("whatsapp-flow-chart") \
            .where("owner_phone_number", "==", str(get_owner_number())) \
            .where("user_message", "==", str(get_user_message())) \
            .limit(1) \
            .get()

        documents = list(reply_message_collection)
        if documents:
            doc_data = documents[0].to_dict()
            update_owner_reply_message(str(doc_data.get("reply_message", "No reply found")).strip())
            update_action(str(doc_data.get("action", "No Action")).strip())

    except Exception as e:
        logger.error(f"Error fetching reply message: {e}")

def process_whatsapp_request():
    action = get_action()

    function_mapping = {
        "send_whatsapp_message": send_whatsapp_message,
        "mark_message_as_read": mark_message_as_read,
        "send_text_message": send_text_message,
        "send_reply_to_message": send_reply_to_message,
        "send_image_message": send_image_message,
        "send_list_message": send_list_message,
        "send_reply_button": send_reply_button,
    }

    if action in function_mapping:
        function_mapping[action]()  
    else:
        logger.error(f"Invalid action specified: {action}")

