from firestore_config import initialize_firebase

def check_record(data):
    db = initialize_firebase()
    if data and "entry" in data:
            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    if "messages" in change.get("value", {}):
                        message = change["value"]["messages"][0]
                        user_number = message["from"]
                        message_id = message["id"]
                        user_message = message.get("text", {}).get("body", "No text message received")
                        owner_phone_number = change["value"]["metadata"]["phone_number_id"]

                        # Save the message to Firestore
                        db.collection("whatsapp-messages").add({
                            "owner_id": owner_phone_number,
                            "user_number": user_number,
                            "user_message": user_message,
                            "message_id": message_id,
                            "created_at": get_current_ist_time()
                        })

                        # Query Firestore to check if the message is already present
                        query = db.collection("whatsapp-messages")\
                                .where("message_id", "==", message_id)\
                                .where("owner_id", "==", owner_phone_number)\
                                .limit(1)\
                                .stream()   

                        # Convert the query to a list and check if it has records
                        record_exists = any(query)
                        logger.info(query)
                        logger.info(record_exists)

                        if record_exists:
                            logger.info("Duplicate message received from WhatsApp: %s", record_exists)
                        else:
                            send_whatsapp_message(user_number, "message", owner_phone_number)
