from firestore_config import initialize_firebase
from datetime import datetime
import logging
from date_utils import *
from global_vars import *

logger = logging.getLogger(__name__)
db = initialize_firebase()


def add_message_to_firestore():

    message_data = {
        "created_date": get_current_ist_time(),
        "owner_number": get_owner_number(),
        "reply_message": get_owner_reply_message(),
        "user_number":get_user_number(),
        "user_message":get_user_message()
    }

    try:
        doc_ref = db.collection("whatsapp-messages").add(message_data)
        logger.info(f"Message document added successfully: {doc_ref}")
        logger.info("added message information database for whatsapp-messages")
        return 
    except Exception as e:
        logger.error(f"Error adding message to Firestore: {e}")
        return {"status": "error", "details": str(e)}

def update_api_execution_log():
    message_data = {
        "created_date": get_current_ist_time(),
        "owner_number": get_owner_number(),
        "user_number":get_user_number(),
        "data":get_data(),
        "stauts":"COMPLETED"
    }

    try:
        doc_ref = db.collection("API-EXECUTION-LOG").add(message_data)
        logger.info(f"Message document added successfully: {doc_ref}")
        logger.info("added message information database for whatsapp-messages")
    except Exception as e:
        logger.error(f"Error adding message to Firestore: {e}")
        return {"status": "error", "details": str(e)}