from firestore_config import initialize_firebase
from date_utils import get_current_ist_time
from api import *
from global_vars import *

import logging

logger = logging.getLogger(__name__)

def process_request():
    logger.info("Inside process request")
    db = initialize_firebase()
    data = get_data()

    if not data or "entry" not in data:
        logger.error("No valid data received in webhook.")
        return 

    for entry in data["entry"]:
        for change in entry.get("changes", []):
            messages = change.get("value", {}).get("messages", [])
            if not messages:
                logger.warning("No messages found in webhook response")
                return

            message = messages[0]

            update_user_number(message["from"])
            update_message_id(message["id"])
            update_user_message(message.get("text", {}).get("body", "No text message received"))
            update_owner_number(change["value"]["metadata"]["phone_number_id"])

            logger.info(f"User Number: {get_user_number()}")
            logger.info(f"Message ID: {get_message_id()}")
            logger.info(f"User Message: {get_user_message()}")
            logger.info(f"Owner Number: {get_owner_number()}")

            query = db.collection("whatsapp-personal-information") \
                .where("phone_number", "==", get_owner_number()) \
                .stream()

            data_list = [doc.to_dict() for doc in query]
            if not data_list:
                logger.error("Owner information not found")
                return

            owner_info = data_list[0]
            update_owner_number(owner_info.get("phone_number", None))
            update_access_key(owner_info.get("key", None))

            reply_message_collection = db.collection("whatsapp-flow-chart") \
                .where("owner_phone_number", "==", str(get_owner_number())) \
                .where("user_message", "==", str(get_user_message())) \
                .limit(1) \
                .get()

            documents = list(reply_message_collection)
            if not documents:
                logger.error("No reply message found")
                return 

            doc_data = documents[0].to_dict()
            update_owner_reply_message(str(doc_data.get("reply_message", "No reply found")).strip())
            update_action(str(doc_data.get("action", "No Action")).strip())

            selectio_of_api()


def selectio_of_api():
    FUNCTION_MAPPING = {
        "send_whatsapp_message": send_whatsapp_message  # ✅ Corrected
    }
    
    api_function = FUNCTION_MAPPING.get(get_action())  # Get the function reference
    
    if api_function:
        response = api_function()  # ✅ Call the function here
        return {"status": "success", "response": response}
    else:
        return {"status": "error", "message": "Invalid option selected"}

