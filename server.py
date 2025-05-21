# Flask backend for Pi user UID storage with template rendering
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import hmac
import hashlib
import os

app = Flask(__name__)
CORS(app)

# Replace with your actual Pi App API secret (store securely!)
API_SECRET = os.getenv('ymsv5rn51qr9afac477bwazqpyq6hxd5hecheslvpnurgehnots7dhs4f6nf8rpw', 'YOUR_PI_APP_API_SECRET')

# Route to render the login template
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to receive authentication payload
@app.route('/store-user', methods=['POST'])
def store_user():
    data = request.get_json()
    # Extract user block
    user = data.get('user', {})
    signature = user.get('signature')
    payload = user.get('payload', {})

    # Recompute HMAC-SHA256 signature
    payload_json = json.dumps(payload, separators=(',', ':'), sort_keys=True)
    expected_sig = hmac.new(
        API_SECRET.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()

    if not signature or not hmac.compare_digest(expected_sig, signature):
        return jsonify({'error': 'Invalid signature'}), 400

    user_uid = user.get('uid')
    username = user.get('username')

    # Append to recipients.json
    entry = {
        'uid': user_uid,
        'username': username,
        'memo': 'Test airdrop',
        'amount': 0.001
    }
    print(f'USER ENTRY: {entry}')
    with open('recipients.json', 'a') as f:
        f.write(json.dumps(entry) + '\n')

    return jsonify({'status': 'stored', 'uid': user_uid}), 200

if __name__ == '__main__':
    # Ensure the templates folder contains index.html
    app.run(host='0.0.0.0', port=5000, debug=True)
