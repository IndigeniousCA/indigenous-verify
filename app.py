from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Indigenous Verify - LIVE!</h1>'

@app.route('/api/verify')
def verify():
    return jsonify({'status': 'API WORKING!', 'message': 'Emergency deployment successful!'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
