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

        logger.info("Received WhatsApp Webhook: %s", data)
        update_data(data)
        logger.info(f"starting : {get_message_id()}")
        logger.info(f"starting: {get_owner_number()}")
        logger.info(f"starting: {get_user_message()}")
        logger.info(f"starting: {get_user_number()}")
        logger.info(f"starting: {get_status()}")


        new_msg_id = get_message_id_from_response(db, get_data())
        logger.info(f"new_msg_id: {new_msg_id}")
        logger.info(f"old emessage id: {get_message_id()}")

        if new_msg_id != get_message_id():
            process_request()
        else:
            logger.info("Duplicate message is detected")

        return {"status": "success"}, 200

    return {"error": "Invalid request method"}, 405
