from firestore_config import initialize_firebase
from date_utils import get_current_ist_time
from api import *
from global_vars import *
import logging

logger = logging.getLogger(__name__)

def process_request():
    """Processes an incoming WhatsApp message request."""
    try:
        db = initialize_firebase()
        results = extract_response(db)

        if results is None or len(results) == 0:  # ✅ Process only if results are empty
            get_owner_information(db)
            get_reply_message(db)

            action = get_action()
            if not action:  # ✅ Ensure action exists before executing API
                logger.warning("No valid action found, skipping API call")
                return

            logger.info(f"Executing action: {action}")

            # ✅ Execute API only once
            response = process_whatsapp_request()
            logger.info(f"API response: {response}")

        else:
            logger.info("Duplicate message received. API will not be called again.")

    except Exception as e:
        logger.error(f"Error processing request: {e}")

def get_owner_information(db):
    try:
        query = db.collection('whatsapp-personal-information') \
            .where('phone_number', '==', get_owner_number()) \
            .get()

        data_list = [doc.to_dict() for doc in query]

        if data_list:
            owner_info = data_list[0]
            update_owner_number(owner_info.get("phone_number", None))
            update_access_key(owner_info.get("key", None))

    except Exception as e:
        logger.error(f"Error fetching data for phone number {get_owner_number()}: {e}")

def get_reply_message(db):
    try:
        reply_message_collection = db.collection("whatsapp-flow-chart") \
            .where("owner_phone_number", "==", get_owner_number()) \
            .where("user_message", "==", get_user_message()) \
            .limit(1) \
            .get()

        documents = list(reply_message_collection)
        if documents:
            doc_data = documents[0].to_dict()
            update_owner_reply_message(doc_data.get("reply_message", "No reply found").strip())
            update_action(doc_data.get("action", "No Action").strip())

    except Exception as e:
        logger.error(f"Error fetching reply message: {e}")

def extract_response(db):
    """Extracts data from the incoming WhatsApp message."""
    try:
        data = get_data()
        processed = False  # ✅ Flag to prevent duplicate execution

        if data and "entry" in data:
            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    if "messages" in change.get("value", {}):
                        if processed:  
                            continue  # ✅ Skip duplicate processing
                        processed = True  # ✅ Mark as processed

                        message = change["value"]["messages"][0]

                        update_user_number(message["from"])
                        update_message_id(message["id"])
                        update_user_message(message.get("text", {}).get("body", "No text message received"))
                        update_owner_number(change["value"]["metadata"]["phone_number_id"])

                        query = db.collection("whatsapp-messages") \
                            .where("message_id", "==", get_message_id()) \
                            .where("owner_id", "==", get_owner_number()) \
                            .limit(1) \
                            .get()

                        results = list(query)
                        if not results:
                            db.collection("whatsapp-execution-logs").add({
                                "api-type": "GET",
                                "response": data,
                                "created-at": get_current_ist_time()
                            })
                        logger.info(results)

                        return results  # ✅ Return results for checking in `process_request()`

    except Exception as e:
        logger.error(f"Error extracting response: {e}")
        return None  # ✅ Explicitly return None if there's an error

def process_whatsapp_request():
    """Calls the respective WhatsApp API function dynamically with the required parameters."""
    
    function_mapping = {
        "send_whatsapp_message": send_whatsapp_message,
        "mark_message_as_read": mark_message_as_read,
        "send_text_message": send_text_message,
        "send_reply_to_message": send_reply_to_message,
        "send_image_message": send_image_message,
        "send_list_message": send_list_message,
        "send_reply_button": send_reply_button,
    }

    action = get_action()
    
    if action in function_mapping:
        try:
            return function_mapping[action]()  # ✅ Call the correct API function
        except Exception as e:
            logger.error(f"Error executing {action}: {e}")
            return {"success": False, "error": str(e)}
    else:
        return {"success": False, "error": "Invalid action specified"}
