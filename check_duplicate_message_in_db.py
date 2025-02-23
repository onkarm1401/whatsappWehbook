from firestore_config import initialize_firebase
from date_utils import get_current_ist_time
from whatsapp_utils import send_whatsapp_message

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
                        query = db.collection("whatsapp-messages")\
                                .where("message_id", "==", message_id)\
                                .where("owner_id", "==", owner_phone_number)\
                                .limit(1)\
                                .stream()

                        # Convert the stream to a list to count the number of results returned
                        results = list(query)

                        record_count = len(results)

                        logger.info("Number of matching records: %d", record_count)

                        if record_count == 1 or record_count == 0:  # If record count is 1, or 0 (no records)
                            send_whatsapp_message(user_number, "message", owner_phone_number)
                        else:
                            logger.info("Duplicate message received from WhatsApp: %d", record_count)


