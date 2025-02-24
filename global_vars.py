# global_vars.py

# Define global variables
owner_number = None
owner_reply_message = None
user_number = None
user_message = None
access_key = None
action = None
message_id = None
data = None

def update_data(new_data):
    global data  
    data = new_data 

def get_data():
    return data

def update_owner_number(new_owner_number):
    global owner_number  
    owner_number = new_owner_number 

def get_owner_number():
    return owner_number

def update_owner_reply_message(new_reply_message):
    global owner_reply_message
    owner_reply_message = new_reply_message

def get_owner_reply_message():
    return owner_reply_message

def update_user_number(new_user_number):
    global user_number
    user_number = new_user_number

def get_user_number():
    return user_number

def update_user_message(new_user_message):
    global user_message
    user_message = new_user_message

def get_user_message():
    return user_message

def update_access_key(new_access_key):
    global access_key
    access_key = new_access_key

def get_access_key():
    return access_key

def update_action(new_action):
    global action
    action = new_action

def get_action():
    return action

def update_message_id(new_message_id):
    global message_id
    message_id = new_message_id

def get_message_id():
    return message_id
