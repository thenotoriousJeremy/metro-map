"""Minimal metro-map app for Raspberry Pi.

Run on the Pi:
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python app.py
"""
import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello from metro-map!'

@app.route('/health')
def health():
    return jsonify(status='ok')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '5000'))
    app.run(host='0.0.0.0', port=port)
