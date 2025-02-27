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
        statuses = data['entry'][0]['changes'][0]['value'].get('statuses')

        if statuses is not None:
            logger.info(f"Started updated status {status}")

            updated_status = status_value = data['entry'][0]['changes'][0]['value'].get('statuses', [{}])[0].get('status', None)
            logger.info(f"updated status is  {updated_status}")

            msg_id = data['entry'][0]['changes'][0]['value']['statuses'][0]['id']
            update_message_id(msg_id)
            docs = db.collection("whatsapp-messages").where("msg_id", "==", str(msg_id)).stream()
            for doc in docs:
                doc.reference.update({
                    'status': updated_status
                })

            logger.info(f"Updated message status{updated_status}")
            return {"status": "Already completed"}, 200

 #       if new_msg_id == last_processed_msg_id:
  #          logger.info("Processing already completed. Stopping execution.")
   #         return {"status": "Already completed"}, 200

        # Step 2: Save the incoming message before processing
        wamid = data['entry'][0]['changes'][0]['value']['messages'][0]['id']        
        msg_occurance = db.collection('whatsapp-messages').where('msg_id', '==', wamid).stream()
        if msg_occurance is None:
            logger.info(f"Duplicate message is recived : {data}")
            return {"status": "Duplicate message"}, 200

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
