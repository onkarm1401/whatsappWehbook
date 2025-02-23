from firestore_config import initialize_firebase
from date_utils import get_current_ist_time

# Initialize Firebase connection
db = initialize_firebase()

def get_information(owner_phone_number):

    info_query = db.collection("whatsapp-personal-information").where("owner_id", "==", owner_phone_number).stream()
    
    # Convert query result into a list of documents
    info_list = [doc.to_dict() for doc in info_query]
    
    # Check if any document found for the owner_phone_number
    if info_list:
        return info_list[0]  # Return the first match (assuming owner_phone_number is unique)
    else:
        return None  # No document found

def get_linked_phone_number(info):
    if info and "phone_number" in info:
        return info["phone_number"]
    return None  # Return None if the field is not found

def get_key_value(info, key):
    """Extracts a specific field value based on the given key."""
    if info and key in info:
        return info[key]
    return None  # Return None if the field is not found
