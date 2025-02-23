from firestore_config import initialize_firebase
from date_utils import get_current_ist_time

# Initialize Firebase connection
db = initialize_firebase()

def get_owner_information(owner_phone_number, key):

    info_query = db.collection("whatsapp-personal-information").where("owner_id", "==", owner_phone_number).stream()
    
    # Convert query result into a list of documents
    info_list = [doc.to_dict() for doc in info_query]
    
    # Check if any document found for the owner_phone_number
    if info_list:
        info = info_list[0]
        
        # Extract linked phone number
        linked_phone_number = info.get("phone_number", None)
        
        # Extract specific key value
        key_value = info.get(key, None)
        
        return {
            "linked_phone_number": linked_phone_number,
            "key_value": key_value
        }
    else:
        return None  # No document found
