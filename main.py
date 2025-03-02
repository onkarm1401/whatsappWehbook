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

#checkpoint for validate message type
        response_check = data['entry'][0]['changes'][0]['value']
                    
#checking status update APi
        if 'statuses' in response_check:  
            statuses = data['entry'][0]['changes'][0]['value'].get('statuses')
            logger.info(f"checking status field in response:  {status}")
            #check send message status like read, delivery
            updated_status = status_value = data['entry'][0]['changes'][0]['value'].get('statuses', [{}])[0].get('status', None)
            logger.info(f"updated status is  {updated_status}")

            msg_id = data['entry'][0]['changes'][0]['value']['statuses'][0]['id']
            update_message_id(msg_id)
            logger.info(f"Message status update for msg if {msg_id}")
            docs = db.collection("whatsapp-messages").where("msg_id", "==", str(msg_id)).stream()
            logger.info(f"Status updated for document id {docs}")
            for doc in docs:
                doc.reference.update({
                    'status': updated_status
                })

            logger.info(f"Updated message status : {updated_status}")
            return {"status": "Already completed"}, 200
 
#checking for response contains message       
        if 'messages' in response_check:
            message = response_check['messages'][0]
            #if response contains interactive object means it is response of previous message.
            if message.get('type') == 'interactive' and 'interactive' in message:  
                button_id = data['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['id']
                button_title = data['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['title']
                logger.info(f"button response is recieved button id : {button_id}")
                if button_id is not None:
                    update_user_message(button_title)
                    update_status("PENDING")
                    update_data(data)
                    update_api_execution_log()

                    update_owner_number(data['entry'][0]['changes'][0]['value']['metadata']['phone_number_id'])
                    update_message_id(data['entry'][0]['changes'][0]['value']['messages'][0]['context']['id'])
                    update_user_number(data['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id'])

                    try:
                        process_request()  # Ensure this runs synchronously
                        logger.info("Request processed successfully.")
                        return {"status": "Processed successfully"}, 200  # ✅ Process completed successfully
                    except Exception as e:
                        logger.error(f"Error processing request: {str(e)}")
                        return {"error": "Processing failed", "details": str(e)}, 500 
            else:
                #new message
                wamid = data['entry'][0]['changes'][0]['value']['messages'][0]['id'] 
                msg_occurance = db.collection('whatsapp-messages').where('msg_id', '==', wamid).stream()
                if msg_occurance is None:
                    logger.info(f"Duplicate message is recived : {data}")
                    return {"status": "Duplicate message"}, 200

                logger.info("started execution")
                update_status("PENDING")
                update_data(data)
                update_api_execution_log()
                
                update_owner_number(data['entry'][0]['changes'][0]['value']['metadata']['phone_number_id'])
                update_user_message(data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body'])
                update_message_id(data['entry'][0]['changes'][0]['value']['messages'][0]['id'])
                update_user_number(data['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id'])

                # Step 3: Process the request synchronously
                try:
                    process_request()  # Ensure this runs synchronously
                    logger.info("Request processed successfully.")
                    return {"status": "Processed successfully"}, 200  # ✅ Process completed successfully
                except Exception as e:
                    logger.error(f"Error processing request: {str(e)}")
                    return {"error": "Processing failed", "details": str(e)}, 500  # ✅ Handle processing errors
        
    return {"error": "Invalid request method"}, 405  # ✅ Handle unsupported HTTP methods
