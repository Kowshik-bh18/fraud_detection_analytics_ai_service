
from flask import Flask, request

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    print("🔥 WEBHOOK RECEIVED:")
    print(request.json)
    return {"status": "ok"}, 200

app.run(port=3000)