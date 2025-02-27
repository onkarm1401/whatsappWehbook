from firestore_config import initialize_firebase
import logging
from date_utils import get_current_ist_time
from global_vars import *

logger = logging.getLogger(__name__)
db = initialize_firebase()

def add_message_to_firestore():
    message_data = {
        "created_date": get_current_ist_time(),
        "owner_number": get_owner_number(),
        "reply_message": get_owner_reply_message(),
        "user_number": get_user_number(),
        "user_message": get_user_message(),
        "msg_id":get_response_id(),
        "status":"Send"

    }

    try:
        # ✅ Ensure synchronous execution by waiting for Firestore operation
        doc_ref = db.collection("whatsapp-messages").document().set(message_data)
        logger.info(f"Message document added successfully")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error adding message to Firestore: {e}")
        return {"status": "error", "details": str(e)}

def update_api_execution_log():
    message_data = {
        "created_date": get_current_ist_time(),
        "owner_number": get_owner_number(),
        "user_number": get_user_number(),
        "data": get_data(),
        "status": "COMPLETED"  # ✅ Fixed spelling error
    }

    try:
        # ✅ Ensure Firestore operation completes before returning
        doc_ref = db.collection("api-execution-log").document().set(message_data)
        logger.info("API Execution Log added successfully")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error adding message to Firestore: {e}")
        return {"status": "error", "details": str(e)}
