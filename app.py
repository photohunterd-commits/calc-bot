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
    ast.Div: operator.truediv
}

def eval_expr(node):
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.BinOp):
        return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
    raise Exception()

def calc(expr):
    tree = ast.parse(expr, mode="eval")
    return eval_expr(tree.body)

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    text = data["payload"]["message"]["text"]
    chat_id = data["payload"]["message"]["chat_id"]

    if text.strip().endswith("="):

        expr = text[:-1].strip()

        try:
            result = calc(expr)

            requests.post(
                "https://api.pachca.com/api/messages",
                json={
                    "chat_id": chat_id,
                    "text": f"{expr} = {result}"
                },
                headers={"Authorization": f"Bearer {BOT_TOKEN}"}
            )

        except:
            pass

    return "ok"

app.run(host="0.0.0.0", port=8080)