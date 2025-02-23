from firestore_config import initialize_firebase
from date_utils import get_current_ist_time
from api import send_whatsapp_message
import logging

logger = logging.getLogger(__name__)

def start_replying(data):
    db = initialize_firebase()
    count_ = check_message_id_in_database(data, db)
    
    if count_ == 1 or count_ == 0:  # If record count is 1 or 0 (no records)
        db.collection("whatsapp-execution-logs").add({
            "api-type": "GET",
            "response": data,
            "created-at": get_current_ist_time()
        })
        execute_response_api(data, db)

def execute_response_api(data, db):
    owner_phone_number = get_owner_number_from_response(data)
    user_number = get_user_number_from_response(data)
    
    info_query = db.collection("whatsapp-personal-information").where("phone_number", "==", owner_phone_number).stream()
    info_list = [doc.to_dict() for doc in info_query]
    logger.info(info_list)
    
    if info_list:
        
        info = info_list[0] 
        linked_phone_number = info.get("phone_number", None)
        key_value = info.get("key_value", None)
        
        response = send_whatsapp_message(user_number, "message", owner_phone_number , key_value)
        text_response = response.text
        db.collection("whatsapp-execution-logs").add({
            "api-type": "POST",
            "response": text_response,
            "created-at": get_current_ist_time()
        })
    else:
        logger.warning(f"No information found for owner: {owner_phone_number}")

def get_owner_number_from_response(data):
    """Extract owner phone number from the response."""
    if data and "entry" in data:
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                if "messages" in change.get("value", {}):
                    return change["value"]["metadata"]["phone_number_id"]
    return None

def get_user_number_from_response(data):
    """Extract user phone number from the response."""
    if data and "entry" in data:
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                if "messages" in change.get("value", {}):
                    return change["value"]["messages"][0]["from"]
    return None

def get_message_id_from_response(data):
    """Extract message ID from the response."""
    if data and "entry" in data:
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                if "messages" in change.get("value", {}):
                    return change["value"]["messages"][0]["id"]
    return None

def get_user_message_response(data):
    """Extract user message from the response."""
    if data and "entry" in data:
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                if "messages" in change.get("value", {}):
                    return change["value"]["messages"][0].get("text", {}).get("body", "No text message received")
    return None

def check_message_id_in_database(data, db):
    """Check if the message ID already exists in the database."""
    message_id = get_message_id_from_response(data)
    owner_phone_number = get_owner_number_from_response(data)
    
    if message_id and owner_phone_number:
        query = db.collection("whatsapp-messages")\
            .where("message_id", "==", message_id)\
            .where("owner_id", "==", owner_phone_number)\
            .limit(1)\
            .stream()

        # Convert the stream to a list to count the number of results returned
        results = list(query)
        record_count = len(results)
        
        logger.info("Number of matching records: %d", record_count)
        return record_count
    
    return 0
