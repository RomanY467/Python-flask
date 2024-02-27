from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    verify_token = os.environ.get('VERIFY_TOKEN')
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode and token:
        if mode == 'subscribe' and token == verify_token:
            print("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            return 'Forbidden', 403
    return 'Not Found', 404

@app.route('/webhook', methods=['POST'])
def webhook():
    body = request.json
    print(body)
    if body.get('object'):
        entry = body.get('entry', [])
        if entry and entry[0].get('changes', []) and entry[0]['changes'][0].get('value', {}).get('messages', []):
            phone_number_id = entry[0]['changes'][0]['value']['metadata']['phone_number_id']
            from_number = entry[0]['changes'][0]['value']['messages'][0]['from']
            msg_body = entry[0]['changes'][0]['value']['messages'][0]['text']['body']
            token = os.environ.get('WHATSAPP_TOKEN')
            url = f"https://graph.facebook.com/v12.0/{phone_number_id}/messages?access_token={token}"
            headers = {'Content-Type': 'application/json'}
            data = {
                "messaging_product": "whatsapp",
                "to": from_number,
                "text": {"body": f"Ack: {msg_body}"}
            }
            response = requests.post(url, json=data, headers=headers)
            return 'OK', 200
    return 'Not Found', 404
  
if __name__ == '__main__':
  app.run(port=int(os.environ.get('PORT', 1337)))
