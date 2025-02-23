import functions_framework
import os
import logging
import requests
from whatsapp_utils import extract_and_log_message  # Importing from the helper file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@functions_framework.http
def whatsapp_webhook(request):
    """Handles WhatsApp webhook verification and incoming messages."""
    if request.method == "GET":
        # Webhook verification
        VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "my_secure_token")
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            logger.info("Webhook verified successfully!")
            return challenge, 200
        return {"error": "Invalid verification token"}, 403

    elif request.method == "POST":
        # Handle incoming messages
        data = request.get_json(silent=True)
        logger.info("Received WhatsApp Webhook: %s", data)

        if data and "entry" in data:
            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    if "messages" in change.get("value", {}):
                        message = change["value"]["messages"][0]
                        sender_id = message["from"]
                        text = message.get("text", {}).get("body", "No text message received")
                        owner_phone_number = change["value"]["metadata"]["phone_number_id"]  # Extracting phone_number_id


                        # Extract and log the message
                        extract_and_log_message(sender_id, text,owner_phone_number)

        return {"status": "received"}, 200

    return {"error": "Invalid request method"}, 405
