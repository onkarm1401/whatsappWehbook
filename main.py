import functions_framework
import os
import logging
from date_utils import get_current_ist_time
from firestore_config import initialize_firebase
from check_duplicate_message_in_db import update_data, get_status, process_request
from global_vars import *
from store_data import *

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

 #       new_msg_id = None  # Initialize the message ID

#        for entry in data.get("entry", []):
 #           for change in entry.get("changes", []):
 #               messages = change.get("value", {}).get("messages", [])
 #              if messages:
   #                 new_msg_id = messages[0]["id"]  # Assuming only one message per request
     #               break  # Stop loop after finding the first message
   #     


        # Step 1: Check if the message has already been processed
        logger.info(f"received data {data}")
        entry_id = update_response_id(data['entry'][0]['id'])
        logger.info(f"response id {entry_id}")

        docs = db.collection("whatsapp-messages").where("msg_id", "==", str(entry_id)).stream()
        logger.info(f"doc against response id :  {docs}")


        found = False
        logger.info(f"Found flag precheck {found}")

        logger.info(found)
        for _ in docs:  # Loop through docs to check if anything exists
            found = True
            break
        logger.info(f"Found flag post check {found}")

        if found:
            logger.info("Inside started to update message status")
            msg_status = status = data['entry'][0]['changes'][0]['value']['statuses'][0]['status']
            logger.info(msg_status)
            db.collection('whatsapp-messages').where('msg_id', '==', entry_id).stream()
            for doc in docs:
                doc.reference.update({
                    'status': msg_status
                })

            logger.info("Ignored as same message is received and updated message status")
            return {"status": "Already completed"}, 200


 #       if new_msg_id == last_processed_msg_id:
  #          logger.info("Processing already completed. Stopping execution.")
   #         return {"status": "Already completed"}, 200

        # Step 2: Save the incoming message before processing
        logger.info("started execution")
        update_status("PENDING")
        update_data(data)
        update_api_execution_log()

        # Step 3: Process the request synchronously
        try:
            process_request()  # Ensure this runs synchronously
            logger.info("Request processed successfully.")
            return {"status": "Processed successfully"}, 200  # ✅ Process completed successfully
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {"error": "Processing failed", "details": str(e)}, 500  # ✅ Handle processing errors

    return {"error": "Invalid request method"}, 405  # ✅ Handle unsupported HTTP methods
