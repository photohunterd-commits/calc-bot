from flask import Flask, request
import requests
import ast
import operator
import os
import json

BOT_TOKEN = (os.environ.get("BOT_TOKEN") or "").strip()

app = Flask(__name__)

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

def eval_expr(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](eval_expr(node.left), eval_expr(node.right))

    if isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.USub):
            return -eval_expr(node.operand)
        if isinstance(node.op, ast.UAdd):
            return eval_expr(node.operand)

    raise ValueError("invalid expression")

def calc(expr: str):
    tree = ast.parse(expr, mode="eval")
    return eval_expr(tree.body)

def send_reply(chat_id: int, parent_message_id: int, text: str):
    url = "https://api.pachca.com/api/shared/v1/messages"
    payload = {
        "message": {
            "entity_type": "discussion",
            "entity_id": chat_id,
            "content": text,
            "parent_message_id": parent_message_id
        }
    }
    headers = {
        "Authorization": f"Bearer {BOT_TOKEN}",
        "Content-Type": "application/json",
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    print("send status:", resp.status_code, resp.text, flush=True)
    resp.raise_for_status()

@app.route("/", methods=["GET"])
def home():
    return "bot running", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    print("incoming:", json.dumps(data, ensure_ascii=False), flush=True)
    print("BOT_TOKEN exists:", bool(BOT_TOKEN), flush=True)
    print("BOT_TOKEN prefix:", BOT_TOKEN[:8], flush=True)

    if data.get("type") != "message":
        return "ok", 200

    if data.get("event") != "new":
        return "ok", 200

    text = (data.get("content") or "").strip()
    chat_id = data.get("chat_id")
    message_id = data.get("id")

    if not text or not chat_id or not message_id:
        return "ok", 200

    if not text.endswith("="):
        return "ok", 200

    expr = text[:-1].strip()
    if not expr:
        return "ok", 200

    try:
        result = calc(expr)
        if isinstance(result, float) and result.is_integer():
            result = int(result)

        send_reply(chat_id, message_id, f"{expr} = {result}")
    except Exception as e:
        print("calc/send error:", repr(e), flush=True)
        try:
            send_reply(chat_id, message_id, "Ошибка вычисления")
        except Exception as send_err:
            print("reply error:", repr(send_err), flush=True)

    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)