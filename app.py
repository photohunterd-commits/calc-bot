from flask import Flask, request
import json
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "bot running", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    print("=== WEBHOOK JSON ===", flush=True)
    print(json.dumps(data, ensure_ascii=False, indent=2), flush=True)
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)