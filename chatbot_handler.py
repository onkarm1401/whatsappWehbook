import requests
import json
import os

def get_openai_key():
    # Ideally fetch from Secret Manager, but for now:
    return os.getenv("OPENAI_API_KEY")

def create_message(thread_id, content):
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_openai_key()}",
        "OpenAI-Beta": "assistants=v2"
    }
    payload = {
        "role": "user",
        "content": content
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

def run_thread(thread_id, assistant_id):
    url = f"https://api.openai.com/v1/threads/{thread_id}/runs"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_openai_key()}",
        "OpenAI-Beta": "assistants=v2"
    }
    payload = {"assistant_id": assistant_id}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

def get_run_status(thread_id, run_id):
    url = f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}"
    headers = {
        "Authorization": f"Bearer {get_openai_key()}",
        "OpenAI-Beta": "assistants=v2"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_message(thread_id, message_id):
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages/{message_id}"
    headers = {
        "Authorization": f"Bearer {get_openai_key()}",
        "OpenAI-Beta": "assistants=v2"
    }
    response = requests.get(url, headers=headers)
    return response.json()
