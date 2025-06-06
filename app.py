from flask import Flask, jsonify, request
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Indigenous Verify API is LIVE!"

@app.route("/api/verify")
def verify():
    bn = request.args.get("bn", "")
    return jsonify({"business_number": bn, "status": "VERIFIED"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
