import functions_framework
import os
import logging
from date_utils import get_current_ist_time
from firestore_config import initialize_firebase
from check_duplicate_message_in_db import update_data, get_status, process_request
from global_vars import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http
def whatsapp_webhook(request):
    db = initialize_firebase()  # Initialize Firebase synchronously

    if request.method == "GET":
        VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "my_secure_token")
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            logger.info("Webhook verified successfully!")
            return challenge, 200  # ✅ Verification successful

        return {"error": "Invalid verification token"}, 403

    elif request.method == "POST":
        data = request.get_json(silent=True)

        if not data:
            logger.warning("Received empty data in webhook")
            return {"error": "Invalid JSON data"}, 400

        logger.info(f"Received WhatsApp Webhook: {data}")

        # Step 1: Check if message has already been processed
        if get_status() == "COMPLETED":
            logger.info("Processing already completed. Stopping execution.")
            return {"status": "Already completed"}, 200

        # Step 2: Save the incoming message before processing
        update_data(data)
        logger.info("Data updated in Firestore.")

        # Step 3: Process the request synchronously
        try:
            process_request()  # This function should execute completely before proceeding
            logger.info("Request processed successfully.")
            return {"status": "Processed successfully"}, 200  # ✅ Process completed successfully
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {"error": "Processing failed", "details": str(e)}, 500  # ✅ Handle processing errors

    return {"error": "Invalid request method"}, 405  # ✅ Handle unsupported HTTP methods
