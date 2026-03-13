from flask import Flask, request
import json

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "bot running", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    print("=== WEBHOOK JSON ===")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return "ok", 200