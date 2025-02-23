from firestore_config import initialize_firebase
from date_utils import get_current_ist_time
from api import send_whatsapp_message
from personal_information import get_owner_information
import logging

logger = logging.getLogger(__name__)


def start_replying(data):
    db = initialize_firebase()
    
    if data and "entry" in data:
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                if "messages" in change.get("value", {}):
                    message = change["value"]["messages"][0]
                    user_number = message["from"]
                    message_id = message["id"]
                    user_message = message.get("text", {}).get("body", "No text message received")
                    owner_phone_number = change["value"]["metadata"]["phone_number_id"]

                    # Save the message to Firestore
                    query = db.collection("whatsapp-messages") \
                        .where("message_id", "==", message_id) \
                        .where("owner_id", "==", owner_phone_number) \
                        .limit(1) \
                        .stream()

                    # Convert the stream to a list to count the number of results returned
                    results = list(query)
                    record_count = len(results)

                    logger.info("Number of matching records: %d", record_count)

                    if record_count == 1 or record_count == 0:  # If record count is 1, or 0 (no records)
                        db.collection("whatsapp-execution-logs").add({
                            "api-type": "GET",
                            "response": data,
                            "created-at": get_current_ist_time()
                        })

                        owner_info = get_owner_information(owner_phone_number)

                        if owner_info:
                            # Extracting linked phone number and key
                            linked_phone_number = owner_info.get("linked_phone_number", None)
                            key_value = owner_info.get("key_value", None)
                        else:
                            print("No information found for the given owner phone number.")

                        response = send_whatsapp_message(user_number, "message", owner_phone_number, key_value)
                        text_response = response.text

                        initialize_firebase().collection("whatsapp-execution-logs").add({
                            "api-type": "POST",
                            "response": text_response,
                            "created-at": get_current_ist_time()
                        })

                        if response.status_code == 200:
                            logger.info(f"Message sent to {user_number} : {message}")
                            users_ref = initialize_firebase().collection("whatsapp-messages")
                            users_ref.add({
                                "owner-number": owner_phone_number,
                                "owner-message": message,
                                "user-number": user_number,
                                "user-message": message,
                                "created-date": get_current_ist_time()
                            })
                        else:
                            logger.error(f"Failed to send message to {user_number}: {response.text}")

                    else:
                        logger.info("Duplicate message received from WhatsApp: %d", record_count)
