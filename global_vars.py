import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Define global variables
owner_number = None
owner_reply_message = None
user_number = None
user_message = None
access_key = None
action = None
message_id = None
data = None
status = None
send_button_menu_options =None

def update_button_menu_option(new_button_options):
    global send_button_menu_options
    send_button_menu_options = new_button_options
    logger.info(f"Updated button menu options: {send_button_menu_options}") 

def get_button_menu_options():
    return send_button_menu_options

def update_status():
    global status
    status = "COMPLETED"
    logger.info(f"Status updated to COMPLETED for message ID: {get_message_id()}")

def get_status():
    return status

def update_data(new_data):
    global data  
    data = new_data
    logger.info(f"Updated data: {data}")

def get_data():
    return data

def update_owner_number(new_owner_number):
    global owner_number  
    owner_number = new_owner_number 
    logger.info(f"Updated owner_number: {owner_number}")

def get_owner_number():
    return owner_number

def update_owner_reply_message(new_reply_message):
    global owner_reply_message
    owner_reply_message = new_reply_message
    logger.info(f"Updated owner_reply_message: {owner_reply_message}")

def get_owner_reply_message():
    return owner_reply_message

def update_user_number(new_user_number):
    global user_number
    user_number = new_user_number
    logger.info(f"Updated user_number: {user_number}")

def get_user_number():
    return user_number

def update_user_message(new_user_message):
    global user_message
    user_message = new_user_message
    logger.info(f"Updated user_message: {user_message}")

def get_user_message():
    return user_message

def update_access_key(new_access_key):
    global access_key
    access_key = new_access_key
    logger.info(f"Updated access_key: {access_key}")

def get_access_key():
    return access_key

def update_action(new_action):
    global action
    action = new_action
    logger.info(f"Updated action: {action}")

def get_action():
    return action

def update_message_id(new_message_id):
    global message_id
    message_id = new_message_id
    logger.info(f"Updated message_id: {message_id}")

def get_message_id():
    return message_id
