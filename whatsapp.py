from flask import Flask, request, jsonify

app = Flask(__name__)

# Webhook verification
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    VERIFY_TOKEN = "my_secure_token"  # Set this in Meta Developer Console
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified successfully!")
        return challenge, 200
    else:
        return "Forbidden", 403

# Handle incoming WhatsApp messages
@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.json
    print("Received WhatsApp Webhook:", data)

    # Process incoming message
    if "entry" in data:
        for entry in data["entry"]:
            for change in entry["changes"]:
                if "messages" in change["value"]:
                    message = change["value"]["messages"][0]
                    sender_id = message["from"]
                    text = message.get("text", {}).get("body", "")

                    print(f"Message from {sender_id}: {text}")
                    
                    # You can process the message and respond here

    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
