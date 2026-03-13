from flask import Flask, request
import requests
import ast
import operator
import os

BOT_TOKEN = os.environ.get("https://api.pachca.com/webhooks/01KKJX2EYTKA175JB4APRCS4HQ")

app = Flask(__name__)

ops = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}

def eval_expr(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.BinOp) and type(node.op) in ops:
        return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -eval_expr(node.operand)
    raise Exception("invalid expression")

def calc(expr):
    tree = ast.parse(expr, mode="eval")
    return eval_expr(tree.body)

@app.route("/", methods=["GET"])
def home():
    return "bot running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    print("incoming:", data)

    if data.get("type") != "message":
        return "ok"

    if data.get("event") != "new":
        return "ok"

    text = (data.get("content") or "").strip()
    chat_id = data.get("chat_id")
    parent_message_id = data.get("id")

    if not text or not chat_id:
        return "ok"

    if text.endswith("="):
        expr = text[:-1].strip()

        if not expr:
            return "ok"

        try:
            result = calc(expr)

            payload = {
                "chat_id": chat_id,
                "content": f"{expr} = {result}",
            }

            r = requests.post(
                "https://api.pachca.com/api/shared/v1/messages",
                json=payload,
                headers={
                    "Authorization": f"Bearer {BOT_TOKEN}",
                    "Content-Type": "application/json",
                },
                timeout=10,
            )
            print("send status:", r.status_code, r.text)

        except Exception as e:
            print("calc/send error:", e)

    return "ok"