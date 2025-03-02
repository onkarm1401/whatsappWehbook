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
            return challenge, 200

        return {"error": "Invalid verification token"}, 403

    elif request.method == "POST":
        data = request.get_json(silent=True)

        if not data:
            logger.warning("Received empty data in webhook")
            return {"error": "Invalid JSON data"}, 400

        logger.info(f"Received WhatsApp Webhook: {data}")

        # Step 1: Check for status updates (message delivery/read status)
        try:
            statuses = data['entry'][0]['changes'][0]['value'].get('statuses')
            logger.info(f"Checking status field in response: {statuses}")

            if statuses:
                updated_status = statuses[0].get('status')
                logger.info(f"Updated status is: {updated_status}")

                msg_id = statuses[0].get('id')
                update_message_id(msg_id)

                logger.info(f"Updating message status for msg_id: {msg_id}")
                docs = db.collection("whatsapp-messages").where("msg_id", "==", str(msg_id)).stream()

                found = False
                for doc in docs:
                    doc.reference.update({'status': updated_status})
                    found = True

                if found:
                    logger.info(f"Message status updated to: {updated_status}")
                    return {"status": "Already completed"}, 200
        except Exception as e:
            logger.error(f"Error updating message status: {str(e)}")

        # Step 2: Handle incoming message (button reply or text message)
        try:
            message = data['entry'][0]['changes'][0]['value']['messages'][0]
            interactive = message.get('interactive', {})
            button_reply = interactive.get('button_reply', {})

            if button_reply:
                button_id = button_reply.get('id')
                button_title = button_reply.get('title')

                logger.info(f"Button response received - button id: {button_id}")

                update_user_message(button_title)
                update_status("PENDING")
                update_data(data)
                update_api_execution_log()

                update_owner_number(data['entry'][0]['changes'][0]['value']['metadata']['phone_number_id'])
                update_message_id(message['context']['id'])
                update_user_number(data['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id'])

                process_request()
                logger.info("Request processed successfully.")
                return {"status": "Processed successfully"}, 200

        except (KeyError, IndexError, TypeError):
            pass  # If button flow fails, fallback to regular message handling

        # Step 3: Handle regular text message (non-button)
        try:
            message = data['entry'][0]['changes'][0]['value']['messages'][0]
            wamid = message.get('id')

            msg_occurance = db.collection('whatsapp-messages').where('msg_id', '==', wamid).stream()
            if any(msg_occurance):
                logger.info(f"Duplicate message received: {wamid}")
                return {"status": "Duplicate message"}, 200

            logger.info("Started execution for regular message flow")

            update_status("PENDING")
            update_data(data)
            update_api_execution_log()

            update_owner_number(data['entry'][0]['changes'][0]['value']['metadata']['phone_number_id'])
            update_user_number(data['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id'])

            if message.get('type') == 'text':
                update_user_message(message['text']['body'])
            else:
                update_user_message("Unsupported message type")

            process_request()
            logger.info("Request processed successfully.")
            return {"status": "Processed successfully"}, 200

        except Exception as e:
            logger.error(f"Error processing regular message: {str(e)}")
            return {"error": "Processing failed", "details": str(e)}, 500

    return {"error": "Invalid request method"}, 405
