import functions_framework
import os
import logging

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

                        logger.info(f"Message from {sender_id}: {text}")
                        
                        # Process the message and respond here

        return {"status": "received"}, 200

    return {"error": "Invalid request method"}, 405
