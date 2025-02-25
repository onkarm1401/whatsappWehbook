from firestore_config import initialize_firebase
from date_utils import get_current_ist_time
from api import *
from global_vars import *

import logging
logger = logging.getLogger(__name__)

def process_request():
    logger.info("inside process request")
    db = initialize_firebase()
    extract_response(db)
   # get_owner_information(db)
  #  get_reply_message(db)
 #   process_whatsapp_request()



def extract_response(db):
    logger.info("inside extract response")
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
                    get_owner_information()

def get_owner_information(db):
    logger.info("inside get owner")
    query = db.collection('whatsapp-personal-information') \
        .where('phone_number', '==', get_owner_number()) \
        .stream()

    data_list = [doc.to_dict() for doc in query]
    if data_list:
        owner_info = data_list[0]
        update_owner_number(owner_info.get("phone_number", None))
        update_access_key(owner_info.get("key", None))
        get_reply_message()
    

def get_reply_message(db):
    logger.info("inside get reply message")
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
        process_whatsapp_request()
    

def process_whatsapp_request():
    logger.info("inside whatsapp request")
    action = get_action()

    if action == "send_whatsapp_message":
        send_whatsapp_message()
    else:
        logger.error(f"Invalid action specified: {action}")

def get_message_id_from_response(db, data):
    logger.info("inside get message id")
    if not data or "entry" not in data:
        return None

    for entry in data["entry"]:
        for change in entry.get("changes", []):
            messages = change.get("value", {}).get("messages", [])
            if messages:
                return messages[0].get("id")  


