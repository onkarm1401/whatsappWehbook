import functions_framework
import os
import logging
import requests
from date_utils  import get_current_ist_time
from whatsapp_utils import send_whatsapp_message
from firestore_config import initialize_firebase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http
def whatsapp_webhook(request):
    """Handles WhatsApp webhook verification and incoming messages."""
    db = initialize_firebase()  # Call Firebase only inside this function

    if request.method == "GET":
        VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "my_secure_token")
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            logger.info("Webhook verified successfully!")
            return challenge, 200
        return {"error": "Invalid verification token"}, 403

    elif request.method == "POST":
        data = request.get_json(silent=True)
        db.collection("whatsapp-execution-logs").add({"api-type": "GET","response": data , "created-at": get_current_ist_time()})
        logger.info("Received WhatsApp Webhook: %s", data)

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
                        db.collection("whatsapp-messages").add({
                            "owner_id": owner_phone_number,
                            "user_number": user_number,
                            "user_message": user_message,
                            "message_id": message_id,
                            "created_at": get_current_ist_time()
                        })

                        # Query Firestore to check if the message is already present
                        query = db.collection("whatsapp-messages")\
                                .where("message_id", "==", message_id)\
                                .where("owner_id", "==", owner_phone_number)\
                                .limit(1)\
                                .stream()   

                        # Convert the query to a list and check if it has records
                        record_exists = any(query)

                        if record_exists:
                            logger.info("Duplicate message received from WhatsApp: %s", data)
                        else:
                            send_whatsapp_message(user_number, "message", owner_phone_number)



        return {"status": "received"}, 200

    return {"error": "Invalid request method"}, 405
