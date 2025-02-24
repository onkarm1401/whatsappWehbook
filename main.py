import functions_framework
import os
import logging
from date_utils import get_current_ist_time
from firestore_config import initialize_firebase
from check_duplicate_message_in_db import process_request
from global_vars import update_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http
def whatsapp_webhook(request):
    """Handles WhatsApp webhook verification and incoming messages."""
    try:
        db = initialize_firebase()

        if request.method == "GET":
            try:
                VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "my_secure_token")
                mode = request.args.get("hub.mode")
                token = request.args.get("hub.verify_token")
                challenge = request.args.get("hub.challenge")

                if mode == "subscribe" and token == VERIFY_TOKEN:
                    logger.info("Webhook verified successfully!")
                    return challenge, 200
                return {"error": "Invalid verification token"}, 403
            except Exception as e:
                logger.error(f"Error during verification: {e}")
                return {"error": "Verification failed"}, 500

        elif request.method == "POST":
            try:
                data = request.get_json(silent=True)
                if not data:
                    logger.warning("Received empty data in webhook")
                    return {"error": "Invalid JSON data"}, 400

                logger.info("Received WhatsApp Webhook: %s", data)
                update_data(data)  # Store data globally
                process_request()
                
            except Exception as e:
                logger.error(f"Error processing webhook data: {e}")
                return {"error": "Webhook processing failed"}, 500

        return {"error": "Invalid request method"}, 405
    except Exception as e:
        logger.critical(f"Unexpected error in webhook: {e}", exc_info=True)
        return {"error": "Internal server error"}, 500
