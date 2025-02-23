import functions_framework
import os
import logging
import requests
from date_utils  import get_current_ist_time
from test_duplicate_records_in_database import check_record
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


        return {"status": "received"}, 200

    return {"error": "Invalid request method"}, 405
