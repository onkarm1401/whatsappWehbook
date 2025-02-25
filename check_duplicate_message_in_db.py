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
        return {"status": "error", "message": "Invalid webhook data"}

    try:
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                messages = change.get("value", {}).get("messages", [])
                if not messages:
                    logger.warning("No messages found in webhook response")
                    return {"status": "error", "message": "No messages found"}

                message = messages[0]

                update_user_number(message["from"])
                update_message_id(message["id"])
                update_user_message(message.get("text", {}).get("body", "No text message received"))
                update_owner_number(change["value"]["metadata"]["phone_number_id"])

                logger.info(f"User Number: {get_user_number()}")
                logger.info(f"Message ID: {get_message_id()}")
                logger.info(f"User Message: {get_user_message()}")
                logger.info(f"Owner Number: {get_owner_number()}")

                # Firestore Query: Fetch Owner Info
                query = db.collection("whatsapp-personal-information") \
                    .where("phone_number", "==", get_owner_number()) \
                    .stream()

                data_list = [doc.to_dict() for doc in query]
                if not data_list:
                    logger.error("Owner information not found")
                    return {"status": "error", "message": "Owner information not found"}

                owner_info = data_list[0]
                update_owner_number(owner_info.get("phone_number", None))
                update_access_key(owner_info.get("key", None))

                # Firestore Query: Fetch Reply Message
                reply_message_collection = db.collection("whatsapp-flow-chart") \
                    .where("owner_phone_number", "==", str(get_owner_number())) \
                    .where("user_message", "==", str(get_user_message())) \
                    .limit(1) \
                    .get()

                documents = list(reply_message_collection)
                if not documents:
                    logger.error("No reply message found")
                    return {"status": "error", "message": "No reply message found"}

                doc_data = documents[0].to_dict()
                update_owner_reply_message(str(doc_data.get("reply_message", "No reply found")).strip())

                # Ensure `button_menu_option` is properly formatted
                button_menu_option = str(doc_data.get("button_menu_option", "")).strip().replace("\\", "")
                update_button_menu_option(button_menu_option)

                update_action(str(doc_data.get("action", "No Action")).strip())

                api_response = selection_of_api()
                
                add_message_to_firestore()
                
                return {"status": "success", "api_response": api_response}
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {"status": "error", "message": str(e)}

def selection_of_api():
    FUNCTION_MAPPING = {
        "send_whatsapp_message": send_whatsapp_message,
        "send_image_message": send_image_message,
        "send_youtube_video": send_youtube_video,
        "send_reply_to_message": send_reply_to_message,
        "send_button_menu": send_button_menu
    }

    api_function = FUNCTION_MAPPING.get(get_action())

    if api_function:
        logger.info(f"Executing API: {get_action()}")
        response = api_function()  # ✅ Ensure the API executes before proceeding
        logger.info(f"API Execution Response: {response}")
        return {"status": "success", "response": response}
    else:
        logger.warning("Invalid API action selected")
        return {"status": "error", "message": "Invalid option selected"}
