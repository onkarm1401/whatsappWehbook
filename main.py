import functions_framework
import os
import logging
from date_utils import get_current_ist_time
from firestore_config import initialize_firebase
from check_duplicate_message_in_db import *
from global_vars import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http 
def whatsapp_webhook(request):
    db = initialize_firebase()

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

        if not data:
            logger.warning("Received empty data in webhook")
            return {"error": "Invalid JSON data"}, 400

        logger.info(f"Received WhatsApp Webhook: {data}")
        update_data(data)

        if get_status() == "COMPLETED":
            logger.info("Processing already completed. Stopping execution.")
            return {"status": "Already completed"}, 200  # ✅ Proper HTTP response

        process_request()
        return {"status": "Processed successfully"}, 200  # ✅ Proper response after execution

    return {"error": "Invalid request method"}, 405  # ✅ Handle unsupported HTTP methods
